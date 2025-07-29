import logging
from typing import TYPE_CHECKING, Any, List, Literal, Optional, Union, Tuple, Callable, overload

if TYPE_CHECKING:
    from natural_pdf.core.page import Page
    from natural_pdf.elements.base import Element as PhysicalElement
    from natural_pdf.elements.collections import ElementCollection as PhysicalElementCollection, PageCollection
    from natural_pdf.elements.region import Region as PhysicalRegion
    from PIL.Image import Image as PIL_Image

    from .collections import FlowElementCollection
    from .element import FlowElement

# Import required classes for the new methods
from natural_pdf.tables import TableResult
# For runtime image manipulation
from PIL import Image as PIL_Image_Runtime

logger = logging.getLogger(__name__)


class Flow:
    """Defines a logical flow or sequence of physical Page or Region objects.

    A Flow represents a continuous logical document structure that spans across
    multiple pages or regions, enabling operations on content that flows across
    boundaries. This is essential for handling multi-page tables, articles that
    span columns, or any content that requires reading order across segments.

    Flows specify arrangement (vertical/horizontal) and alignment rules to create
    a unified coordinate system for element extraction and text processing. They
    enable natural-pdf to treat fragmented content as a single continuous area
    for analysis and extraction operations.

    The Flow system is particularly useful for:
    - Multi-page tables that break across page boundaries
    - Multi-column articles with complex reading order
    - Forms that span multiple pages
    - Any content requiring logical continuation across segments

    Attributes:
        segments: List of Page or Region objects in flow order.
        arrangement: Primary flow direction ('vertical' or 'horizontal').
        alignment: Cross-axis alignment for segments of different sizes.
        segment_gap: Virtual gap between segments in PDF points.

    Example:
        Multi-page table flow:
        ```python
        pdf = npdf.PDF("multi_page_table.pdf")

        # Create flow for table spanning pages 2-4
        table_flow = Flow(
            segments=[pdf.pages[1], pdf.pages[2], pdf.pages[3]],
            arrangement='vertical',
            alignment='left',
            segment_gap=10.0
        )

        # Extract table as if it were continuous
        table_data = table_flow.extract_table()
        text_content = table_flow.get_text()
        ```

        Multi-column article flow:
        ```python
        page = pdf.pages[0]
        left_column = page.region(0, 0, 300, page.height)
        right_column = page.region(320, 0, page.width, page.height)

        # Create horizontal flow for columns
        article_flow = Flow(
            segments=[left_column, right_column],
            arrangement='horizontal',
            alignment='top'
        )

        # Read in proper order
        article_text = article_flow.get_text()
        ```

    Note:
        Flows create virtual coordinate systems that map element positions across
        segments, enabling spatial navigation and element selection to work
        seamlessly across boundaries.
    """

    def __init__(
        self,
        segments: Union[List[Union["Page", "PhysicalRegion"]], "PageCollection"],
        arrangement: Literal["vertical", "horizontal"],
        alignment: Literal["start", "center", "end", "top", "left", "bottom", "right"] = "start",
        segment_gap: float = 0.0,
    ):
        """
        Initializes a Flow object.

        Args:
            segments: An ordered list of natural_pdf.core.page.Page or
                      natural_pdf.elements.region.Region objects that constitute the flow,
                      or a PageCollection containing pages.
            arrangement: The primary direction of the flow.
                         - "vertical": Segments are stacked top-to-bottom.
                         - "horizontal": Segments are arranged left-to-right.
            alignment: How segments are aligned on their cross-axis if they have
                       differing dimensions. For a "vertical" arrangement:
                       - "left" (or "start"): Align left edges.
                       - "center": Align centers.
                       - "right" (or "end"): Align right edges.
                       For a "horizontal" arrangement:
                       - "top" (or "start"): Align top edges.
                       - "center": Align centers.
                       - "bottom" (or "end"): Align bottom edges.
            segment_gap: The virtual gap (in PDF points) between segments.
        """
        # Handle PageCollection input
        if hasattr(segments, 'pages'):  # It's a PageCollection
            segments = list(segments.pages)
        
        if not segments:
            raise ValueError("Flow segments cannot be empty.")
        if arrangement not in ["vertical", "horizontal"]:
            raise ValueError("Arrangement must be 'vertical' or 'horizontal'.")

        self.segments: List["PhysicalRegion"] = self._normalize_segments(segments)
        self.arrangement: Literal["vertical", "horizontal"] = arrangement
        self.alignment: Literal["start", "center", "end", "top", "left", "bottom", "right"] = (
            alignment
        )
        self.segment_gap: float = segment_gap

        self._validate_alignment()

        # TODO: Pre-calculate segment offsets for faster lookups if needed

    def _normalize_segments(
        self, segments: List[Union["Page", "PhysicalRegion"]]
    ) -> List["PhysicalRegion"]:
        """Converts all Page segments to full-page Region objects for uniform processing."""
        normalized = []
        from natural_pdf.core.page import Page as CorePage
        from natural_pdf.elements.region import Region as ElementsRegion

        for i, segment in enumerate(segments):
            if isinstance(segment, CorePage):
                normalized.append(segment.region(0, 0, segment.width, segment.height))
            elif isinstance(segment, ElementsRegion):
                normalized.append(segment)
            elif hasattr(segment, "object_type") and segment.object_type == "page":
                if not isinstance(segment, CorePage):
                    raise TypeError(
                        f"Segment {i} has object_type 'page' but is not an instance of natural_pdf.core.page.Page. Got {type(segment)}"
                    )
                normalized.append(segment.region(0, 0, segment.width, segment.height))
            elif hasattr(segment, "object_type") and segment.object_type == "region":
                if not isinstance(segment, ElementsRegion):
                    raise TypeError(
                        f"Segment {i} has object_type 'region' but is not an instance of natural_pdf.elements.region.Region. Got {type(segment)}"
                    )
                normalized.append(segment)
            else:
                raise TypeError(
                    f"Segment {i} is not a valid Page or Region object. Got {type(segment)}."
                )
        return normalized

    def _validate_alignment(self) -> None:
        """Validates the alignment based on the arrangement."""
        valid_alignments = {
            "vertical": ["start", "center", "end", "left", "right"],
            "horizontal": ["start", "center", "end", "top", "bottom"],
        }
        if self.alignment not in valid_alignments[self.arrangement]:
            raise ValueError(
                f"Invalid alignment '{self.alignment}' for '{self.arrangement}' arrangement. "
                f"Valid options are: {valid_alignments[self.arrangement]}"
            )

    def find(
        self,
        selector: Optional[str] = None,
        *,
        text: Optional[str] = None,
        apply_exclusions: bool = True,
        regex: bool = False,
        case: bool = True,
        **kwargs,
    ) -> Optional["FlowElement"]:
        """
        Finds the first element within the flow that matches the given selector or text criteria.

        Elements found are wrapped as FlowElement objects, anchored to this Flow.

        Args:
            selector: CSS-like selector string.
            text: Text content to search for.
            apply_exclusions: Whether to respect exclusion zones on the original pages/regions.
            regex: Whether the text search uses regex.
            case: Whether the text search is case-sensitive.
            **kwargs: Additional filter parameters for the underlying find operation.

        Returns:
            A FlowElement if a match is found, otherwise None.
        """
        results = self.find_all(
            selector=selector,
            text=text,
            apply_exclusions=apply_exclusions,
            regex=regex,
            case=case,
            **kwargs,
        )
        return results.first if results else None

    def find_all(
        self,
        selector: Optional[str] = None,
        *,
        text: Optional[str] = None,
        apply_exclusions: bool = True,
        regex: bool = False,
        case: bool = True,
        **kwargs,
    ) -> "FlowElementCollection":
        """
        Finds all elements within the flow that match the given selector or text criteria.
        
        This method efficiently groups segments by their parent pages, searches at the page level,
        then filters results appropriately for each segment. This ensures elements that intersect
        with flow segments (but aren't fully contained) are still found.
        
        Elements found are wrapped as FlowElement objects, anchored to this Flow,
        and returned in a FlowElementCollection.
        """
        from .collections import FlowElementCollection
        from .element import FlowElement

        # Step 1: Group segments by their parent pages (like in analyze_layout)
        segments_by_page = {}  # Dict[Page, List[Segment]]
        
        for i, segment in enumerate(self.segments):
            # Determine the page for this segment - fix type detection
            if hasattr(segment, 'page') and hasattr(segment.page, 'find_all'):
                # It's a Region object (has a parent page)
                page_obj = segment.page
                segment_type = "region"
            elif hasattr(segment, 'find_all') and hasattr(segment, 'width') and hasattr(segment, 'height') and not hasattr(segment, 'page'):
                # It's a Page object (has find_all but no parent page)
                page_obj = segment
                segment_type = "page"
            else:
                logger.warning(f"Segment {i+1} does not support find_all, skipping")
                continue
            
            if page_obj not in segments_by_page:
                segments_by_page[page_obj] = []
            segments_by_page[page_obj].append((segment, segment_type))

        if not segments_by_page:
            logger.warning("No segments with searchable pages found")
            return FlowElementCollection([])

        # Step 2: Search each unique page only once
        all_flow_elements: List["FlowElement"] = []

        for page_obj, page_segments in segments_by_page.items():
            # Find all matching elements on this page
            page_matches = page_obj.find_all(
                selector=selector,
                text=text,
                apply_exclusions=apply_exclusions,
                regex=regex,
                case=case,
                **kwargs,
            )
            
            if not page_matches:
                continue

            # Step 3: For each segment on this page, collect relevant elements
            for segment, segment_type in page_segments:
                if segment_type == "page":
                    # Full page segment: include all elements
                    for phys_elem in page_matches.elements:
                        all_flow_elements.append(FlowElement(physical_object=phys_elem, flow=self))
                
                elif segment_type == "region":
                    # Region segment: filter to only intersecting elements
                    for phys_elem in page_matches.elements:
                        try:
                            # Check if element intersects with this flow segment
                            if segment.intersects(phys_elem):
                                all_flow_elements.append(FlowElement(physical_object=phys_elem, flow=self))
                        except Exception as intersect_error:
                            logger.debug(f"Error checking intersection for element: {intersect_error}")
                            # Include the element anyway if intersection check fails
                            all_flow_elements.append(FlowElement(physical_object=phys_elem, flow=self))

        # Step 4: Remove duplicates (can happen if multiple segments intersect the same element)
        unique_flow_elements = []
        seen_element_ids = set()
        
        for flow_elem in all_flow_elements:
            # Create a unique identifier for the underlying physical element
            phys_elem = flow_elem.physical_object
            elem_id = (
                getattr(phys_elem.page, 'index', id(phys_elem.page)) if hasattr(phys_elem, 'page') else id(phys_elem),
                phys_elem.bbox if hasattr(phys_elem, 'bbox') else id(phys_elem)
            )
            
            if elem_id not in seen_element_ids:
                unique_flow_elements.append(flow_elem)
                seen_element_ids.add(elem_id)

        return FlowElementCollection(unique_flow_elements)

    def __repr__(self) -> str:
        return (
            f"<Flow segments={len(self.segments)}, "
            f"arrangement='{self.arrangement}', alignment='{self.alignment}', gap={self.segment_gap}>"
        )

    @overload
    def extract_table(
        self,
        method: Optional[str] = None,
        table_settings: Optional[dict] = None,
        use_ocr: bool = False,
        ocr_config: Optional[dict] = None,
        text_options: Optional[dict] = None,
        cell_extraction_func: Optional[Any] = None,
        show_progress: bool = False,
        content_filter: Optional[Any] = None,
        stitch_rows: Callable[[List[Optional[str]]], bool] = None,
    ) -> TableResult: ...

    @overload
    def extract_table(
        self,
        method: Optional[str] = None,
        table_settings: Optional[dict] = None,
        use_ocr: bool = False,
        ocr_config: Optional[dict] = None,
        text_options: Optional[dict] = None,
        cell_extraction_func: Optional[Any] = None,
        show_progress: bool = False,
        content_filter: Optional[Any] = None,
        stitch_rows: Callable[
            [List[Optional[str]], List[Optional[str]], int, Union["Page", "PhysicalRegion"]],
            bool,
        ] = None,
    ) -> TableResult: ...

    def extract_table(
        self,
        method: Optional[str] = None,
        table_settings: Optional[dict] = None,
        use_ocr: bool = False,
        ocr_config: Optional[dict] = None,
        text_options: Optional[dict] = None,
        cell_extraction_func: Optional[Any] = None,
        show_progress: bool = False,
        content_filter: Optional[Any] = None,
        stitch_rows: Optional[Callable] = None,
    ) -> TableResult:
        """
        Extract table data from all segments in the flow, combining results sequentially.

        This method extracts table data from each segment in flow order and combines
        the results into a single logical table. This is particularly useful for
        multi-page tables or tables that span across columns.

        Args:
            method: Method to use: 'tatr', 'pdfplumber', 'text', 'stream', 'lattice', or None (auto-detect).
            table_settings: Settings for pdfplumber table extraction.
            use_ocr: Whether to use OCR for text extraction (currently only applicable with 'tatr' method).
            ocr_config: OCR configuration parameters.
            text_options: Dictionary of options for the 'text' method.
            cell_extraction_func: Optional callable function that takes a cell Region object
                                  and returns its string content. For 'text' method only.
            show_progress: If True, display a progress bar during cell text extraction for the 'text' method.
            content_filter: Optional content filter to apply during cell text extraction.
            stitch_rows: Optional callable to determine when rows should be merged across
                         segment boundaries. Two overloaded signatures are supported:
                         
                         • func(current_row) -> bool
                           Called only on the first row of each segment (after the first).
                           Return True to merge this first row with the last row from
                           the previous segment.
                           
                         • func(prev_row, current_row, row_index, segment) -> bool
                           Called for every row. Return True to merge current_row with
                           the previous row in the aggregated results.
                           
                         When True is returned, rows are concatenated cell-by-cell.
                         This is useful for handling table rows split across page
                         boundaries or segments. If None, rows are never merged.

        Returns:
            TableResult object containing the aggregated table data from all segments.

        Example:
            Multi-page table extraction:
            ```python
            pdf = npdf.PDF("multi_page_table.pdf")
            
            # Create flow for table spanning pages 2-4
            table_flow = Flow(
                segments=[pdf.pages[1], pdf.pages[2], pdf.pages[3]],
                arrangement='vertical'
            )
            
            # Extract table as if it were continuous
            table_data = table_flow.extract_table()
            df = table_data.df  # Convert to pandas DataFrame
            
            # Custom row stitching - single parameter (simple case)
            table_data = table_flow.extract_table(
                stitch_rows=lambda row: row and not (row[0] or "").strip()
            )
            
            # Custom row stitching - full parameters (advanced case)
            table_data = table_flow.extract_table(
                stitch_rows=lambda prev, curr, idx, seg: idx == 0 and curr and not (curr[0] or "").strip()
            )
            ```
        """
        logger.info(f"Extracting table from Flow with {len(self.segments)} segments (method: {method or 'auto'})")
        
        if not self.segments:
            logger.warning("Flow has no segments, returning empty table")
            return TableResult([])

        # Resolve predicate and determine its signature
        predicate: Optional[Callable] = None
        predicate_type: str = "none"
        
        if callable(stitch_rows):
            import inspect
            sig = inspect.signature(stitch_rows)
            param_count = len(sig.parameters)
            
            if param_count == 1:
                predicate = stitch_rows
                predicate_type = "single_param"
            elif param_count == 4:
                predicate = stitch_rows
                predicate_type = "full_params"
            else:
                logger.warning(f"stitch_rows function has {param_count} parameters, expected 1 or 4. Ignoring.")
                predicate = None
                predicate_type = "none"

        def _default_merge(prev_row: List[Optional[str]], cur_row: List[Optional[str]]) -> List[Optional[str]]:
            from itertools import zip_longest
            merged: List[Optional[str]] = []
            for p, c in zip_longest(prev_row, cur_row, fillvalue=""):
                if (p or "").strip() and (c or "").strip():
                    merged.append(f"{p} {c}".strip())
                else:
                    merged.append((p or "") + (c or ""))
            return merged

        aggregated_rows: List[List[Optional[str]]] = []
        processed_segments = 0

        for seg_idx, segment in enumerate(self.segments):
            try:
                logger.debug(f"  Extracting table from segment {seg_idx+1}/{len(self.segments)}")

                segment_result = segment.extract_table(
                    method=method,
                    table_settings=table_settings.copy() if table_settings else None,
                    use_ocr=use_ocr,
                    ocr_config=ocr_config,
                    text_options=text_options.copy() if text_options else None,
                    cell_extraction_func=cell_extraction_func,
                    show_progress=show_progress,
                    content_filter=content_filter,
                )

                if not segment_result:
                    continue

                if hasattr(segment_result, "_rows"):
                    segment_rows = list(segment_result._rows)
                else:
                    segment_rows = list(segment_result)

                if not segment_rows:
                    logger.debug(f"    No table data found in segment {seg_idx+1}")
                    continue

                for row_idx, row in enumerate(segment_rows):
                    should_merge = False
                    
                    if predicate is not None and aggregated_rows:
                        if predicate_type == "single_param":
                            # For single param: only call on first row of segment (row_idx == 0)
                            # and pass the current row
                            if row_idx == 0:
                                should_merge = predicate(row)
                        elif predicate_type == "full_params":
                            # For full params: call with all arguments
                            should_merge = predicate(aggregated_rows[-1], row, row_idx, segment)
                    
                    if should_merge:
                        aggregated_rows[-1] = _default_merge(aggregated_rows[-1], row)
                    else:
                        aggregated_rows.append(row)

                processed_segments += 1
                logger.debug(f"    Added {len(segment_rows)} rows (post-merge) from segment {seg_idx+1}")

            except Exception as e:
                logger.error(f"Error extracting table from segment {seg_idx+1}: {e}", exc_info=True)
                continue

        logger.info(
            f"Flow table extraction complete: {len(aggregated_rows)} total rows from {processed_segments}/{len(self.segments)} segments"
        )
        return TableResult(aggregated_rows)

    def analyze_layout(
        self,
        engine: Optional[str] = None,
        options: Optional[Any] = None,
        confidence: Optional[float] = None,
        classes: Optional[List[str]] = None,
        exclude_classes: Optional[List[str]] = None,
        device: Optional[str] = None,
        existing: str = "replace",
        model_name: Optional[str] = None,
        client: Optional[Any] = None,
    ) -> "PhysicalElementCollection":
        """
        Analyze layout across all segments in the flow.

        This method efficiently groups segments by their parent pages, runs layout analysis
        only once per unique page, then filters results appropriately for each segment.
        This avoids redundant analysis when multiple flow segments come from the same page.

        Args:
            engine: Name of the layout engine (e.g., 'yolo', 'tatr'). Uses manager's default if None.
            options: Specific LayoutOptions object for advanced configuration.
            confidence: Minimum confidence threshold.
            classes: Specific classes to detect.
            exclude_classes: Classes to exclude.
            device: Device for inference.
            existing: How to handle existing detected regions: 'replace' (default) or 'append'.
            model_name: Optional model name for the engine.
            client: Optional client for API-based engines.

        Returns:
            ElementCollection containing all detected Region objects from all segments.

        Example:
            Multi-page layout analysis:
            ```python
            pdf = npdf.PDF("document.pdf")
            
            # Create flow for first 3 pages
            page_flow = Flow(
                segments=pdf.pages[:3],
                arrangement='vertical'
            )
            
            # Analyze layout across all pages (efficiently)
            all_regions = page_flow.analyze_layout(engine='yolo')
            
            # Find all tables across the flow
            tables = all_regions.filter('region[type=table]')
            ```
        """
        from natural_pdf.elements.collections import ElementCollection
        
        logger.info(f"Analyzing layout across Flow with {len(self.segments)} segments (engine: {engine or 'default'})")
        
        if not self.segments:
            logger.warning("Flow has no segments, returning empty collection")
            return ElementCollection([])

        # Step 1: Group segments by their parent pages to avoid redundant analysis
        segments_by_page = {}  # Dict[Page, List[Segment]]
        
        for i, segment in enumerate(self.segments):
            # Determine the page for this segment
            if hasattr(segment, 'analyze_layout'):
                # It's a Page object
                page_obj = segment
                segment_type = "page"
            elif hasattr(segment, 'page') and hasattr(segment.page, 'analyze_layout'):
                # It's a Region object
                page_obj = segment.page
                segment_type = "region"
            else:
                logger.warning(f"Segment {i+1} does not support layout analysis, skipping")
                continue
            
            if page_obj not in segments_by_page:
                segments_by_page[page_obj] = []
            segments_by_page[page_obj].append((segment, segment_type))

        if not segments_by_page:
            logger.warning("No segments with analyzable pages found")
            return ElementCollection([])

        logger.debug(f"  Grouped {len(self.segments)} segments into {len(segments_by_page)} unique pages")

        # Step 2: Analyze each unique page only once
        all_detected_regions: List["PhysicalRegion"] = []
        processed_pages = 0

        for page_obj, page_segments in segments_by_page.items():
            try:
                logger.debug(f"  Analyzing layout for page {getattr(page_obj, 'number', '?')} with {len(page_segments)} segments")
                
                # Run layout analysis once for this page
                page_results = page_obj.analyze_layout(
                    engine=engine,
                    options=options,
                    confidence=confidence,
                    classes=classes,
                    exclude_classes=exclude_classes,
                    device=device,
                    existing=existing,
                    model_name=model_name,
                    client=client,
                )

                # Extract regions from results
                if hasattr(page_results, 'elements'):
                    # It's an ElementCollection
                    page_regions = page_results.elements
                elif isinstance(page_results, list):
                    # It's a list of regions
                    page_regions = page_results
                else:
                    logger.warning(f"Page {getattr(page_obj, 'number', '?')} returned unexpected layout analysis result type: {type(page_results)}")
                    continue

                if not page_regions:
                    logger.debug(f"    No layout regions found on page {getattr(page_obj, 'number', '?')}")
                    continue

                # Step 3: For each segment on this page, collect relevant regions
                segments_processed_on_page = 0
                for segment, segment_type in page_segments:
                    if segment_type == "page":
                        # Full page segment: include all detected regions
                        all_detected_regions.extend(page_regions)
                        segments_processed_on_page += 1
                        logger.debug(f"    Added {len(page_regions)} regions for full-page segment")
                    
                    elif segment_type == "region":
                        # Region segment: filter to only intersecting regions
                        intersecting_regions = []
                        for region in page_regions:
                            try:
                                if segment.intersects(region):
                                    intersecting_regions.append(region)
                            except Exception as intersect_error:
                                logger.debug(f"Error checking intersection for region: {intersect_error}")
                                # Include the region anyway if intersection check fails
                                intersecting_regions.append(region)
                        
                        all_detected_regions.extend(intersecting_regions)
                        segments_processed_on_page += 1
                        logger.debug(f"    Added {len(intersecting_regions)} intersecting regions for region segment {segment.bbox}")

                processed_pages += 1
                logger.debug(f"    Processed {segments_processed_on_page} segments on page {getattr(page_obj, 'number', '?')}")

            except Exception as e:
                logger.error(f"Error analyzing layout for page {getattr(page_obj, 'number', '?')}: {e}", exc_info=True)
                continue

        # Step 4: Remove duplicates (can happen if multiple segments intersect the same region)
        unique_regions = []
        seen_region_ids = set()
        
        for region in all_detected_regions:
            # Create a unique identifier for this region (page + bbox)
            region_id = (
                getattr(region.page, 'index', id(region.page)),
                region.bbox if hasattr(region, 'bbox') else id(region)
            )
            
            if region_id not in seen_region_ids:
                unique_regions.append(region)
                seen_region_ids.add(region_id)

        dedupe_removed = len(all_detected_regions) - len(unique_regions)
        if dedupe_removed > 0:
            logger.debug(f"  Removed {dedupe_removed} duplicate regions")

        logger.info(f"Flow layout analysis complete: {len(unique_regions)} unique regions from {processed_pages} pages")
        return ElementCollection(unique_regions)

    def show(
        self,
        resolution: Optional[float] = None,
        labels: bool = True,
        legend_position: str = "right",
        color: Optional[Union[Tuple, str]] = "blue",
        label_prefix: Optional[str] = "FlowSegment",
        width: Optional[int] = None,
        stack_direction: str = "vertical",
        stack_gap: int = 5,
        stack_background_color: Tuple[int, int, int] = (255, 255, 255),
        crop: bool = False,
        **kwargs,
    ) -> Optional["PIL_Image"]:
        """
        Generates and returns a PIL Image showing all segments in the flow with highlights.

        This method visualizes the entire flow by highlighting each segment on its respective
        page and combining the results into a single image. If multiple pages are involved,
        they are stacked according to the flow's arrangement.

        Args:
            resolution: Resolution in DPI for page rendering. If None, uses global setting or defaults to 144 DPI.
            labels: Whether to include a legend for highlights.
            legend_position: Position of the legend ('right', 'bottom', 'top', 'left').
            color: Color for highlighting the flow segments.
            label_prefix: Prefix for segment labels (e.g., 'FlowSegment').
            width: Optional width for the output image (overrides resolution).
            stack_direction: Direction to stack multiple pages ('vertical' or 'horizontal').
            stack_gap: Gap in pixels between stacked pages.
            stack_background_color: RGB background color for the stacked image.
            crop: If True, crop each rendered page to the bounding box of segments on that page.
            **kwargs: Additional arguments passed to the underlying rendering methods.

        Returns:
            PIL Image of the rendered pages with highlighted flow segments, or None if rendering fails.

        Example:
            Visualizing a multi-page flow:
            ```python
            pdf = npdf.PDF("document.pdf")
            
            # Create flow across multiple pages
            page_flow = Flow(
                segments=[pdf.pages[0], pdf.pages[1], pdf.pages[2]],
                arrangement='vertical'
            )
            
            # Show the entire flow
            flow_image = page_flow.show(color="green", labels=True)
            ```
        """
        logger.info(f"Rendering Flow with {len(self.segments)} segments")
        
        if not self.segments:
            logger.warning("Flow has no segments to show")
            return None

        # Apply global options as defaults for resolution
        import natural_pdf
        if resolution is None:
            if natural_pdf.options.image.resolution is not None:
                resolution = natural_pdf.options.image.resolution
            else:
                resolution = 144  # Default resolution

        # 1. Group segments by their physical pages
        segments_by_page = {}  # Dict[Page, List[PhysicalRegion]]
        
        for i, segment in enumerate(self.segments):
            # Get the page for this segment
            if hasattr(segment, 'page') and segment.page is not None:
                # It's a Region, use its page
                page_obj = segment.page
                if page_obj not in segments_by_page:
                    segments_by_page[page_obj] = []
                segments_by_page[page_obj].append(segment)
            elif hasattr(segment, 'index') and hasattr(segment, 'width') and hasattr(segment, 'height'):
                # It's a full Page object, create a full-page region for it
                page_obj = segment
                full_page_region = segment.region(0, 0, segment.width, segment.height)
                if page_obj not in segments_by_page:
                    segments_by_page[page_obj] = []
                segments_by_page[page_obj].append(full_page_region)
            else:
                logger.warning(f"Segment {i+1} has no identifiable page, skipping")
                continue

        if not segments_by_page:
            logger.warning("No segments with identifiable pages found")
            return None

        # 2. Get a highlighter service from the first page
        first_page = next(iter(segments_by_page.keys()))
        if not hasattr(first_page, '_highlighter'):
            logger.error("Cannot get highlighter service for Flow.show(). Page missing highlighter.")
            return None
        
        highlighter_service = first_page._highlighter
        output_page_images: List["PIL_Image_Runtime"] = []

        # Sort pages by index for consistent output order
        sorted_pages = sorted(
            segments_by_page.keys(),
            key=lambda p: p.index if hasattr(p, "index") else getattr(p, "page_number", 0),
        )

        # 3. Render each page with its relevant segments highlighted
        for page_idx, page_obj in enumerate(sorted_pages):
            segments_on_this_page = segments_by_page[page_obj]
            if not segments_on_this_page:
                continue

            temp_highlights_for_page = []
            for i, segment in enumerate(segments_on_this_page):
                segment_label = None
                if labels and label_prefix:
                    # Create label for this segment
                    global_segment_idx = None
                    try:
                        # Find the global index of this segment in the original flow
                        global_segment_idx = self.segments.index(segment)
                    except ValueError:
                        # If it's a generated full-page region, find its source page
                        for idx, orig_segment in enumerate(self.segments):
                            if (hasattr(orig_segment, 'index') and hasattr(segment, 'page') 
                                and orig_segment.index == segment.page.index):
                                global_segment_idx = idx
                                break
                    
                    if global_segment_idx is not None:
                        segment_label = f"{label_prefix}_{global_segment_idx + 1}"
                    else:
                        segment_label = f"{label_prefix}_p{page_idx + 1}s{i + 1}"

                temp_highlights_for_page.append(
                    {
                        "page_index": (
                            page_obj.index
                            if hasattr(page_obj, "index")
                            else getattr(page_obj, "page_number", 1) - 1
                        ),
                        "bbox": segment.bbox,
                        "polygon": segment.polygon if hasattr(segment, 'polygon') and hasattr(segment, 'has_polygon') and segment.has_polygon else None,
                        "color": color,
                        "label": segment_label,
                        "use_color_cycling": False,  # Keep specific color
                    }
                )

            if not temp_highlights_for_page:
                continue

            # Calculate crop bbox if cropping is enabled
            crop_bbox = None
            if crop and segments_on_this_page:
                # Calculate the bounding box that encompasses all segments on this page
                min_x0 = min(segment.bbox[0] for segment in segments_on_this_page)
                min_y0 = min(segment.bbox[1] for segment in segments_on_this_page)
                max_x1 = max(segment.bbox[2] for segment in segments_on_this_page)
                max_y1 = max(segment.bbox[3] for segment in segments_on_this_page)
                crop_bbox = (min_x0, min_y0, max_x1, max_y1)

            # Render this page with highlights
            page_image = highlighter_service.render_preview(
                page_index=(
                    page_obj.index
                    if hasattr(page_obj, "index")
                    else getattr(page_obj, "page_number", 1) - 1
                ),
                temporary_highlights=temp_highlights_for_page,
                resolution=resolution,
                width=width,
                labels=labels,
                legend_position=legend_position,
                crop_bbox=crop_bbox,
                **kwargs,
            )
            if page_image:
                output_page_images.append(page_image)

        # 4. Stack the generated page images if multiple
        if not output_page_images:
            logger.warning("Flow.show() produced no page images")
            return None

        if len(output_page_images) == 1:
            return output_page_images[0]

        # Determine stacking direction (default to flow arrangement, but allow override)
        final_stack_direction = stack_direction
        if stack_direction == "auto":
            final_stack_direction = self.arrangement

        # Stack multiple page images
        if final_stack_direction == "vertical":
            final_width = max(img.width for img in output_page_images)
            final_height = (
                sum(img.height for img in output_page_images)
                + (len(output_page_images) - 1) * stack_gap
            )
            if final_width == 0 or final_height == 0:
                raise ValueError("Cannot create concatenated image with zero width or height.")

            concatenated_image = PIL_Image_Runtime.new(
                "RGB", (final_width, final_height), stack_background_color
            )
            current_y = 0
            for img in output_page_images:
                paste_x = (final_width - img.width) // 2
                concatenated_image.paste(img, (paste_x, current_y))
                current_y += img.height + stack_gap
            return concatenated_image
            
        elif final_stack_direction == "horizontal":
            final_width = (
                sum(img.width for img in output_page_images)
                + (len(output_page_images) - 1) * stack_gap
            )
            final_height = max(img.height for img in output_page_images)
            if final_width == 0 or final_height == 0:
                raise ValueError("Cannot create concatenated image with zero width or height.")

            concatenated_image = PIL_Image_Runtime.new(
                "RGB", (final_width, final_height), stack_background_color
            )
            current_x = 0
            for img in output_page_images:
                paste_y = (final_height - img.height) // 2
                concatenated_image.paste(img, (current_x, paste_y))
                current_x += img.width + stack_gap
            return concatenated_image
        else:
            raise ValueError(
                f"Invalid stack_direction '{final_stack_direction}' for Flow.show(). Must be 'vertical' or 'horizontal'."
            )

    # --- Helper methods for coordinate transformations and segment iteration ---
    # These will be crucial for FlowElement's directional methods.

    def get_segment_bounding_box_in_flow(
        self, segment_index: int
    ) -> Optional[tuple[float, float, float, float]]:
        """
        Calculates the conceptual bounding box of a segment within the flow's coordinate system.
        This considers arrangement, alignment, and segment gaps.
        (This is a placeholder for more complex logic if a true virtual coordinate system is needed)
        For now, it might just return the physical segment's bbox if gaps are 0 and alignment is simple.
        """
        if segment_index < 0 or segment_index >= len(self.segments):
            return None

        # This is a simplified version. A full implementation would calculate offsets.
        # For now, we assume FlowElement directional logic handles segment traversal and uses physical coords.
        # If we were to *draw* the flow or get a FlowRegion bbox that spans gaps, this would be critical.
        # physical_segment = self.segments[segment_index]
        # return physical_segment.bbox
        raise NotImplementedError(
            "Calculating a segment's bbox *within the flow's virtual coordinate system* is not yet fully implemented."
        )

    def get_element_flow_coordinates(
        self, physical_element: "PhysicalElement"
    ) -> Optional[tuple[float, float, float, float]]:
        """
        Translates a physical element's coordinates into the flow's virtual coordinate system.
        (Placeholder - very complex if segment_gap > 0 or complex alignments)
        """
        # For now, elements operate in their own physical coordinates. This method would be needed
        # if FlowRegion.bbox or other operations needed to present a unified coordinate space.
        # As per our discussion, elements *within* a FlowRegion retain original physical coordinates.
        # So, this might not be strictly necessary for the current design's core functionality.
        raise NotImplementedError(
            "Translating element coordinates to a unified flow coordinate system is not yet implemented."
        )
