"""Direct API methods for supported document processing tools.

This file provides convenient methods that wrap the Nutrient Build API
for supported document processing operations.
"""

from typing import TYPE_CHECKING, Any, Protocol

from nutrient_dws.file_handler import FileInput

if TYPE_CHECKING:
    from nutrient_dws.builder import BuildAPIWrapper
    from nutrient_dws.http_client import HTTPClient


class HasBuildMethod(Protocol):
    """Protocol for objects that have a build method."""

    def build(self, input_file: FileInput) -> "BuildAPIWrapper":
        """Build method signature."""
        ...

    @property
    def _http_client(self) -> "HTTPClient":
        """HTTP client property."""
        ...


class DirectAPIMixin:
    """Mixin class containing Direct API methods.

    These methods provide a simplified interface to common document
    processing operations. They internally use the Build API.

    Note: The API automatically converts supported document formats
    (DOCX, XLSX, PPTX) to PDF when processing.
    """

    def _process_file(
        self,
        tool: str,
        input_file: FileInput,
        output_path: str | None = None,
        **options: Any,
    ) -> bytes | None:
        """Process file method that will be provided by NutrientClient."""
        raise NotImplementedError("This method is provided by NutrientClient")

    def convert_to_pdf(
        self,
        input_file: FileInput,
        output_path: str | None = None,
    ) -> bytes | None:
        """Convert a document to PDF.

        Converts Office documents (DOCX, XLSX, PPTX) to PDF format.
        This uses the API's implicit conversion - simply uploading a
        non-PDF document returns it as a PDF.

        Args:
            input_file: Input document (DOCX, XLSX, PPTX, etc).
            output_path: Optional path to save the output PDF.

        Returns:
            Converted PDF as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors (e.g., unsupported format).

        Note:
            HTML files are not currently supported by the API.
        """
        # Use builder with no actions - implicit conversion happens
        # Type checking: at runtime, self is NutrientClient which has these methods
        return self.build(input_file).execute(output_path)  # type: ignore[attr-defined,no-any-return]

    def flatten_annotations(
        self, input_file: FileInput, output_path: str | None = None
    ) -> bytes | None:
        """Flatten annotations and form fields in a PDF.

        Converts all annotations and form fields into static page content.
        If input is an Office document, it will be converted to PDF first.

        Args:
            input_file: Input file (PDF or Office document).
            output_path: Optional path to save the output file.

        Returns:
            Processed file as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
        """
        return self._process_file("flatten-annotations", input_file, output_path)

    def rotate_pages(
        self,
        input_file: FileInput,
        output_path: str | None = None,
        degrees: int = 0,
        page_indexes: list[int] | None = None,
    ) -> bytes | None:
        """Rotate pages in a PDF.

        Rotate all pages or specific pages by the specified degrees.
        If input is an Office document, it will be converted to PDF first.

        Args:
            input_file: Input file (PDF or Office document).
            output_path: Optional path to save the output file.
            degrees: Rotation angle (90, 180, 270, or -90).
            page_indexes: Optional list of page indexes to rotate (0-based).

        Returns:
            Processed file as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
        """
        options = {"degrees": degrees}
        if page_indexes is not None:
            options["page_indexes"] = page_indexes  # type: ignore
        return self._process_file("rotate-pages", input_file, output_path, **options)

    def ocr_pdf(
        self,
        input_file: FileInput,
        output_path: str | None = None,
        language: str = "english",
    ) -> bytes | None:
        """Apply OCR to a PDF to make it searchable.

        Performs optical character recognition on the PDF to extract text
        and make it searchable. If input is an Office document, it will
        be converted to PDF first.

        Args:
            input_file: Input file (PDF or Office document).
            output_path: Optional path to save the output file.
            language: OCR language. Supported: "english", "eng", "deu", "german".
                     Default is "english".

        Returns:
            Processed file as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
        """
        return self._process_file("ocr-pdf", input_file, output_path, language=language)

    def watermark_pdf(
        self,
        input_file: FileInput,
        output_path: str | None = None,
        text: str | None = None,
        image_url: str | None = None,
        image_file: FileInput | None = None,
        width: int = 200,
        height: int = 100,
        opacity: float = 1.0,
        position: str = "center",
    ) -> bytes | None:
        """Add a watermark to a PDF.

        Adds a text or image watermark to all pages of the PDF.
        If input is an Office document, it will be converted to PDF first.

        Args:
            input_file: Input file (PDF or Office document).
            output_path: Optional path to save the output file.
            text: Text to use as watermark. One of text, image_url, or image_file required.
            image_url: URL of image to use as watermark.
            image_file: Local image file to use as watermark (path, bytes, or file-like object).
                       Supported formats: PNG, JPEG, TIFF.
            width: Width of the watermark in points (required).
            height: Height of the watermark in points (required).
            opacity: Opacity of the watermark (0.0 to 1.0).
            position: Position of watermark. One of: "top-left", "top-center",
                     "top-right", "center", "bottom-left", "bottom-center",
                     "bottom-right".

        Returns:
            Processed file as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
            ValueError: If none of text, image_url, or image_file is provided.
        """
        if not text and not image_url and not image_file:
            raise ValueError("Either text, image_url, or image_file must be provided")

        # For image file uploads, we need to use the builder directly
        if image_file:
            from nutrient_dws.file_handler import prepare_file_for_upload, save_file_output

            # Prepare files for upload
            files = {}

            # Main PDF file
            file_field, file_data = prepare_file_for_upload(input_file, "file")
            files[file_field] = file_data

            # Watermark image file
            image_field, image_data = prepare_file_for_upload(image_file, "watermark")
            files[image_field] = image_data

            # Build instructions with watermark action
            action = {
                "type": "watermark",
                "width": width,
                "height": height,
                "opacity": opacity,
                "position": position,
                "image": "watermark",  # Reference to the uploaded image file
            }

            instructions = {"parts": [{"file": "file"}], "actions": [action]}

            # Make API request
            # Type checking: at runtime, self is NutrientClient which has _http_client
            result = self._http_client.post(  # type: ignore[attr-defined]
                "/build",
                files=files,
                json_data=instructions,
            )

            # Handle output
            if output_path:
                save_file_output(result, output_path)
                return None
            else:
                return result  # type: ignore[no-any-return]

        # For text and URL watermarks, use the existing _process_file approach
        options = {
            "width": width,
            "height": height,
            "opacity": opacity,
            "position": position,
        }

        if text:
            options["text"] = text
        else:
            options["image_url"] = image_url

        return self._process_file("watermark-pdf", input_file, output_path, **options)

    def apply_redactions(
        self,
        input_file: FileInput,
        output_path: str | None = None,
    ) -> bytes | None:
        """Apply redaction annotations to permanently remove content.

        Applies any redaction annotations in the PDF to permanently remove
        the underlying content. If input is an Office document, it will
        be converted to PDF first.

        Args:
            input_file: Input file (PDF or Office document).
            output_path: Optional path to save the output file.

        Returns:
            Processed file as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
        """
        return self._process_file("apply-redactions", input_file, output_path)

    def create_redactions_preset(
        self,
        input_file: FileInput,
        preset: str,
        output_path: str | None = None,
        include_annotations: bool = False,
        appearance_fill_color: str | None = None,
        appearance_stroke_color: str | None = None,
    ) -> bytes | None:
        """Create redaction annotations using a preset pattern.

        Creates redaction annotations for common sensitive data patterns
        like social security numbers, credit card numbers, etc.

        Args:
            input_file: Input PDF file.
            preset: Preset pattern to use. Valid options:
                - "social-security-number": US Social Security Number
                - "credit-card-number": Credit card numbers
                - "international-phone-number": International phone numbers
                - "north-american-phone-number": North America phone numbers
                - "date": Date patterns
                - "time": Time patterns
                - "us-zip-code": US Zip Code patterns
                - "email-address": Email addresses
            output_path: Optional path to save the output file.
            include_annotations: Include text in annotations (default: False).
            appearance_fill_color: Fill color for redaction boxes (hex format).
            appearance_stroke_color: Stroke color for redaction boxes (hex format).

        Returns:
            PDF with redaction annotations as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.

        Note:
            This creates redaction annotations but does not apply them.
            Use apply_redactions() to permanently remove the content.
        """
        options = {
            "strategy": "preset",
            "strategy_options": {
                "preset": preset,
                "includeAnnotations": include_annotations,
            },
        }

        # Add appearance options if provided
        content = {}
        if appearance_fill_color:
            content["fillColor"] = appearance_fill_color
        if appearance_stroke_color:
            content["outlineColor"] = appearance_stroke_color

        if content:
            options["content"] = content

        return self._process_file("create-redactions", input_file, output_path, **options)

    def create_redactions_regex(
        self,
        input_file: FileInput,
        pattern: str,
        output_path: str | None = None,
        case_sensitive: bool = False,
        include_annotations: bool = False,
        appearance_fill_color: str | None = None,
        appearance_stroke_color: str | None = None,
    ) -> bytes | None:
        """Create redaction annotations using a regex pattern.

        Creates redaction annotations for text matching a regular expression.

        Args:
            input_file: Input PDF file.
            pattern: Regular expression pattern to match.
            output_path: Optional path to save the output file.
            case_sensitive: Whether pattern matching is case-sensitive (default: False).
            include_annotations: Include text in annotations (default: False).
            include_text: Include regular text content (default: True).
            appearance_fill_color: Fill color for redaction boxes (hex format).
            appearance_stroke_color: Stroke color for redaction boxes (hex format).

        Returns:
            PDF with redaction annotations as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.

        Note:
            This creates redaction annotations but does not apply them.
            Use apply_redactions() to permanently remove the content.
        """
        options = {
            "strategy": "regex",
            "strategy_options": {
                "regex": pattern,
                "caseSensitive": case_sensitive,
                "includeAnnotations": include_annotations,
            },
        }

        # Add appearance options if provided
        content = {}
        if appearance_fill_color:
            content["fillColor"] = appearance_fill_color
        if appearance_stroke_color:
            content["outlineColor"] = appearance_stroke_color

        if content:
            options["content"] = content

        return self._process_file("create-redactions", input_file, output_path, **options)

    def create_redactions_text(
        self,
        input_file: FileInput,
        text: str,
        output_path: str | None = None,
        case_sensitive: bool = True,
        include_annotations: bool = False,
        appearance_fill_color: str | None = None,
        appearance_stroke_color: str | None = None,
    ) -> bytes | None:
        """Create redaction annotations for exact text matches.

        Creates redaction annotations for all occurrences of specific text.

        Args:
            input_file: Input PDF file.
            text: Exact text to redact.
            output_path: Optional path to save the output file.
            case_sensitive: Whether text matching is case-sensitive (default: True).
            include_annotations: Include text in annotations (default: False).
            appearance_fill_color: Fill color for redaction boxes (hex format).
            appearance_stroke_color: Stroke color for redaction boxes (hex format).

        Returns:
            PDF with redaction annotations as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.

        Note:
            This creates redaction annotations but does not apply them.
            Use apply_redactions() to permanently remove the content.
        """
        options = {
            "strategy": "text",
            "strategy_options": {
                "text": text,
                "caseSensitive": case_sensitive,
                "includeAnnotations": include_annotations,
            },
        }

        # Add appearance options if provided
        content = {}
        if appearance_fill_color:
            content["fillColor"] = appearance_fill_color
        if appearance_stroke_color:
            content["outlineColor"] = appearance_stroke_color

        if content:
            options["content"] = content

        return self._process_file("create-redactions", input_file, output_path, **options)

    def optimize_pdf(
        self,
        input_file: FileInput,
        output_path: str | None = None,
        grayscale_text: bool = False,
        grayscale_graphics: bool = False,
        grayscale_images: bool = False,
        grayscale_form_fields: bool = False,
        grayscale_annotations: bool = False,
        disable_images: bool = False,
        mrc_compression: bool = False,
        image_optimization_quality: int | None = 2,
        linearize: bool = False,
    ) -> bytes | None:
        """Optimize a PDF to reduce file size.

        Applies various optimization techniques to reduce the file size of a PDF
        while maintaining readability. If input is an Office document, it will
        be converted to PDF first.

        Args:
            input_file: Input file (PDF or Office document).
            output_path: Optional path to save the output file.
            grayscale_text: Convert text to grayscale (default: False).
            grayscale_graphics: Convert graphics to grayscale (default: False).
            grayscale_images: Convert images to grayscale (default: False).
            grayscale_form_fields: Convert form_fields to grayscale (default: False).
            grayscale_annotations: Convert annotations to grayscale (default: False).
            disable_images: Remove all images from the PDF (default: False).
            mrc_compression: MCR compression (default: False).
            image_optimization_quality: Image optimization quality from 1 (least optimized)
             to 4 (most optimized) (default: 2).
            linearize: Linearize (optimize for web viewing) the PDF (default: False).

        Returns:
            Optimized PDF as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
            ValueError: If image_optimization_quality is not between 1-4
            or no optimization is enabled

        Example:
            # Aggressive optimization for minimum file size
            client.optimize_pdf(
                "large_document.pdf",
                grayscale_images=True,
                image_optimization_quality=4,
                output_path="optimized.pdf"
            )
        """
        options: dict[str, Any] = {}

        # Add grayscale options
        if grayscale_text:
            options["grayscale_text"] = True
        if grayscale_graphics:
            options["grayscale_graphics"] = True
        if grayscale_images:
            options["grayscale_images"] = True
        if grayscale_form_fields:
            options["grayscale_form_fields"] = True
        if grayscale_annotations:
            options["grayscale_annotations"] = True

        # Add MCR compression
        if mrc_compression:
            options["mrc_compression"] = True

        # Add image options
        if disable_images:
            options["disable_images"] = True
        if image_optimization_quality is not None:
            if not 1 <= image_optimization_quality <= 4:
                raise ValueError("image_optimization_quality must be between 1 and 4")
            options["image_optimization_quality"] = image_optimization_quality

        # Add linearization
        if linearize:
            options["linearize"] = True

        # Build using the Builder API with output options
        builder = self.build(input_file)  # type: ignore[attr-defined]

        # Apply optimization via output options
        if options:
            # If there are specific options, set optimize to the options dict
            builder.set_output_options(optimize=options)
        else:
            # If no options, raise error
            raise ValueError("No optimization is enabled")
        return builder.execute(output_path)  # type: ignore[no-any-return]

    def password_protect_pdf(
        self,
        input_file: FileInput,
        output_path: str | None = None,
        user_password: str | None = None,
        owner_password: str | None = None,
        permissions: list[str] | None = None,
    ) -> bytes | None:
        """Add password protection and permissions to a PDF.

        Secures a PDF with password protection and optional permission restrictions.
        If input is an Office document, it will be converted to PDF first.

        Args:
            input_file: Input file (PDF or Office document).
            output_path: Optional path to save the output file.
            user_password: Password required to open the document.
            owner_password: Password required to change permissions/security settings.
                            If not provided, uses user_password.
            permissions: Array of permission strings. Available permissions:
                - "printing": Allow printing
                - "modification": Allow document modification
                - "extract": Allow content extraction
                - "annotations_and_forms": Allow adding annotations
                - "fill_forms": Allow filling forms
                - "extract_accessibility": Allow accessibility features
                - "assemble": Allow document assembly
                - "print_high_quality": Allow high-quality printing

        Returns:
            Protected PDF as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
            ValueError: If neither user_password nor owner_password is provided.

        Example:
            # Protect with view-only permissions (only allowing extract_accessibility)
            client.password_protect_pdf(
                "sensitive.pdf",
                user_password="view123",
                owner_password="admin456",
                permissions=["extract_accessibility"],
                output_path="protected.pdf"
            )
        """
        if not user_password and not owner_password:
            raise ValueError("At least one of user_password or owner_password must be provided")

        # Build using the Builder API with output options
        builder = self.build(input_file)  # type: ignore[attr-defined]

        # Set up password options with camelCase for API
        password_options: dict[str, Any] = {}
        if user_password:
            password_options["userPassword"] = user_password
        if owner_password:
            password_options["ownerPassword"] = owner_password
        else:
            # If no owner password provided, use user password
            password_options["ownerPassword"] = user_password

        # Set up permissions if provided
        if permissions:
            password_options["permissions"] = permissions

        # Apply password protection via output options
        builder.set_output_options(**password_options)
        return builder.execute(output_path)  # type: ignore[no-any-return]

    def set_pdf_metadata(
        self,
        input_file: FileInput,
        output_path: str | None = None,
        title: str | None = None,
        author: str | None = None,
    ) -> bytes | None:
        """Set metadata properties of a PDF.

        Updates the metadata/document properties of a PDF file.
        If input is an Office document, it will be converted to PDF first.
        Only title and author metadata fields are supported.

        Args:
            input_file: Input file (PDF or Office document).
            output_path: Optional path to save the output file.
            title: Document title.
            author: Document author.

        Returns:
            PDF with updated metadata as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
            ValueError: If no metadata fields are provided.

        Example:
            client.set_pdf_metadata(
                "document.pdf",
                title="Annual Report 2024",
                author="John Doe",
                output_path="document_with_metadata.pdf"
            )
        """
        metadata = {}
        if title is not None:
            metadata["title"] = title
        if author is not None:
            metadata["author"] = author

        if not metadata:
            raise ValueError("At least one metadata field must be provided")

        # Build using the Builder API with output options
        builder = self.build(input_file)  # type: ignore[attr-defined]
        builder.set_output_options(metadata=metadata)
        return builder.execute(output_path)  # type: ignore[no-any-return]

    def split_pdf(
        self,
        input_file: FileInput,
        page_ranges: list[dict[str, int]] | None = None,
        output_paths: list[str] | None = None,
    ) -> list[bytes]:
        """Split a PDF into multiple documents by page ranges.

        Splits a PDF into multiple files based on specified page ranges.
        Each range creates a separate output file.

        Args:
            input_file: Input PDF file.
            page_ranges: List of page range dictionaries. Each dict can contain:
                - 'start': Starting page index (0-based, inclusive)
                - 'end': Ending page index (0-based, inclusive)
                - If not provided, splits into individual pages
            output_paths: Optional list of paths to save output files.
                          Must match length of page_ranges if provided.

        Returns:
            List of PDF bytes for each split, or empty list if output_paths provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
            ValueError: If page_ranges and output_paths length mismatch.

        Examples:
            # Split into individual pages
            pages = client.split_pdf("document.pdf")

            # Split by custom ranges
            parts = client.split_pdf(
                "document.pdf",
                page_ranges=[
                    {"start": 0, "end": 4},      # Pages 1-5
                    {"start": 5, "end": 9},      # Pages 6-10
                    {"start": 10}                # Pages 11 to end
                ]
            )

            # Save to specific files
            client.split_pdf(
                "document.pdf",
                page_ranges=[{"start": 0, "end": 1}, {"start": 2}],
                output_paths=["part1.pdf", "part2.pdf"]
            )
        """
        from nutrient_dws.file_handler import (
            get_pdf_page_count,
            prepare_file_for_upload,
            save_file_output,
        )

        # Validate inputs
        if not page_ranges:
            # Default behavior: extract first page only
            page_ranges = [{"start": 0, "end": 0}]

        if len(page_ranges) > 50:
            raise ValueError("Maximum 50 page ranges allowed")

        if output_paths and len(output_paths) != len(page_ranges):
            raise ValueError("output_paths length must match page_ranges length")

        # Get total number of pages to validate ranges
        num_of_pages = get_pdf_page_count(input_file)

        # Validate and adjust page ranges
        for i, page_range in enumerate(page_ranges):
            start = page_range.get("start", 0)

            # Validate start is within document bounds
            if start < 0 or start >= num_of_pages:
                raise ValueError(
                    f"Page range {i}: start index {start} is out of bounds (0-{num_of_pages - 1})"
                )

            # If end is specified, validate it's within document bounds
            if "end" in page_range:
                end = page_range["end"]
                if end < 0 or end >= num_of_pages:
                    raise ValueError(
                        f"Page range {i}: end index {end} is out of bounds (0-{num_of_pages - 1})"
                    )
                if end < start:
                    raise ValueError(
                        f"Page range {i}: end index {end} cannot be less than start index {start}"
                    )

        results = []

        # Process each page range as a separate API call
        for i, page_range in enumerate(page_ranges):
            # Prepare file for upload
            file_field, file_data = prepare_file_for_upload(input_file, "file")
            files = {file_field: file_data}

            # Build instructions for page extraction
            instructions = {"parts": [{"file": "file", "pages": page_range}], "actions": []}

            # Make API request
            # Type checking: at runtime, self is NutrientClient which has _http_client
            result = self._http_client.post(  # type: ignore[attr-defined]
                "/build",
                files=files,
                json_data=instructions,
            )

            # Handle output
            if output_paths and i < len(output_paths):
                save_file_output(result, output_paths[i])
            else:
                results.append(result)  # type: ignore[arg-type]

        return results if not output_paths else []

    def duplicate_pdf_pages(
        self,
        input_file: FileInput,
        page_indexes: list[int],
        output_path: str | None = None,
    ) -> bytes | None:
        """Duplicate specific pages within a PDF document.

        Creates a new PDF containing the specified pages in the order provided.
        Pages can be duplicated multiple times by including their index multiple times.

        Args:
            input_file: Input PDF file.
            page_indexes: List of page indexes to include (0-based).
                         Pages can be repeated to create duplicates.
                         Negative indexes are supported (-1 for last page).
            output_path: Optional path to save the output file.

        Returns:
            Processed PDF as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
            ValueError: If page_indexes is empty.

        Examples:
            # Duplicate first page twice, then include second page
            result = client.duplicate_pdf_pages(
                "document.pdf",
                page_indexes=[0, 0, 1]  # Page 1, Page 1, Page 2
            )

            # Include last page at beginning and end
            result = client.duplicate_pdf_pages(
                "document.pdf",
                page_indexes=[-1, 0, 1, 2, -1]  # Last, First, Second, Third, Last
            )

            # Save to specific file
            client.duplicate_pdf_pages(
                "document.pdf",
                page_indexes=[0, 2, 1],  # Reorder: Page 1, Page 3, Page 2
                output_path="reordered.pdf"
            )
        """
        from nutrient_dws.file_handler import (
            get_pdf_page_count,
            prepare_file_for_upload,
            save_file_output,
        )

        # Validate inputs
        if not page_indexes:
            raise ValueError("page_indexes cannot be empty")

        # Prepare file for upload
        file_field, file_data = prepare_file_for_upload(input_file, "file")
        files = {file_field: file_data}

        # Get total number of pages to validate indexes
        num_of_pages = get_pdf_page_count(input_file)

        # Build parts for each page index
        parts = []
        for page_index in page_indexes:
            if page_index < 0:
                # For negative indexes, use the index directly (API supports negative indexes)
                # No validation for negative indexes as they're handled by the API
                parts.append({"file": "file", "pages": {"start": page_index, "end": page_index}})
            else:
                # Validate positive indexes are within bounds
                if page_index >= num_of_pages:
                    raise ValueError(
                        f"Page index {page_index} is out of bounds (0-{num_of_pages - 1})"
                    )
                # For positive indexes, create single-page range
                parts.append({"file": "file", "pages": {"start": page_index, "end": page_index}})

        # Build instructions for duplication
        instructions = {"parts": parts, "actions": []}

        # Make API request
        # Type checking: at runtime, self is NutrientClient which has _http_client
        result = self._http_client.post(  # type: ignore[attr-defined]
            "/build",
            files=files,
            json_data=instructions,
        )

        # Handle output
        if output_path:
            save_file_output(result, output_path)
            return None
        else:
            return result  # type: ignore[no-any-return]

    def delete_pdf_pages(
        self,
        input_file: FileInput,
        page_indexes: list[int],
        output_path: str | None = None,
    ) -> bytes | None:
        """Delete specific pages from a PDF document.

        Creates a new PDF with the specified pages removed. The API approach
        works by selecting all pages except those to be deleted.

        Args:
            input_file: Input PDF file.
            page_indexes: List of page indexes to delete (0-based). 0 = first page.
                         Must be unique, sorted in ascending order.
                         Negative indexes are NOT supported.
            output_path: Optional path to save the output file.

        Returns:
            Processed PDF as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
            ValueError: If page_indexes is empty or contains negative indexes.

        Examples:
            # Delete first and last pages (Note: negative indexes not supported)
            result = client.delete_pdf_pages(
                "document.pdf",
                page_indexes=[0, 2]  # Delete pages 1 and 3
            )

            # Delete specific pages (2nd and 4th pages)
            result = client.delete_pdf_pages(
                "document.pdf",
                page_indexes=[1, 3]  # 0-based indexing
            )

            # Save to specific file
            client.delete_pdf_pages(
                "document.pdf",
                page_indexes=[2, 4, 5],
                output_path="pages_deleted.pdf"
            )
        """
        from nutrient_dws.file_handler import (
            get_pdf_page_count,
            prepare_file_for_upload,
            save_file_output,
        )

        # Validate inputs
        if not page_indexes:
            raise ValueError("page_indexes cannot be empty")

        # Check for negative indexes
        if any(idx < 0 for idx in page_indexes):
            negative_indexes = [idx for idx in page_indexes if idx < 0]
            raise ValueError(
                f"Negative page indexes not yet supported for deletion: {negative_indexes}"
            )

        # Get total number of pages to validate indexes
        num_of_pages = get_pdf_page_count(input_file)

        # Validate page indexes are within bounds
        for idx in page_indexes:
            if idx >= num_of_pages:
                raise ValueError(f"Page index {idx} is out of bounds (0-{num_of_pages - 1})")

        # Prepare file for upload
        file_field, file_data = prepare_file_for_upload(input_file, "file")
        files = {file_field: file_data}

        # Sort page indexes to handle ranges efficiently
        sorted_indexes = sorted(set(page_indexes))  # Remove duplicates and sort

        # Build parts for pages to keep (excluding the ones to delete)
        # We need to create ranges that exclude the deleted pages
        parts = []

        # Start from page 0
        current_page = 0

        for delete_index in sorted_indexes:
            # Add range from current_page to delete_index-1 (inclusive)
            if current_page < delete_index:
                parts.append(
                    {"file": "file", "pages": {"start": current_page, "end": delete_index - 1}}
                )

            # Skip the deleted page
            current_page = delete_index + 1

        # Add remaining pages after the last deleted page
        num_of_pages = get_pdf_page_count(input_file)
        if (
            current_page > 0 or (current_page == 0 and len(sorted_indexes) == 0)
        ) and current_page < num_of_pages:
            # Add all remaining pages from current_page onwards
            parts.append({"file": "file", "pages": {"start": current_page}})

        # If no parts, it means we're trying to delete all pages
        if not parts:
            raise ValueError("Cannot delete all pages from document")

        # Build instructions for deletion (keeping non-deleted pages)
        instructions = {"parts": parts, "actions": []}

        # Make API request
        # Type checking: at runtime, self is NutrientClient which has _http_client
        result = self._http_client.post(  # type: ignore[attr-defined]
            "/build",
            files=files,
            json_data=instructions,
        )

        # Handle output
        if output_path:
            save_file_output(result, output_path)
            return None
        else:
            return result  # type: ignore[no-any-return]

    def merge_pdfs(
        self,
        input_files: list[FileInput],
        output_path: str | None = None,
    ) -> bytes | None:
        """Merge multiple PDF files into one.

        Combines multiple files into a single PDF in the order provided.
        Office documents (DOCX, XLSX, PPTX) will be automatically converted
        to PDF before merging.

        Args:
            input_files: List of input files (PDFs or Office documents).
            output_path: Optional path to save the output file.

        Returns:
            Merged PDF as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
            ValueError: If less than 2 files provided.

        Example:
            # Merge PDFs and Office documents
            client.merge_pdfs([
                "document1.pdf",
                "document2.docx",
                "spreadsheet.xlsx"
            ], "merged.pdf")
        """
        if len(input_files) < 2:
            raise ValueError("At least 2 files required for merge")

        from nutrient_dws.file_handler import prepare_file_for_upload, save_file_output

        # Prepare files for upload
        files = {}
        parts = []

        for i, file in enumerate(input_files):
            field_name = f"file{i}"
            file_field, file_data = prepare_file_for_upload(file, field_name)
            files[file_field] = file_data
            parts.append({"file": field_name})

        # Build instructions for merge (no actions needed)
        instructions = {"parts": parts, "actions": []}

        # Make API request
        # Type checking: at runtime, self is NutrientClient which has _http_client
        result = self._http_client.post(  # type: ignore[attr-defined]
            "/build",
            files=files,
            json_data=instructions,
        )

        # Handle output
        if output_path:
            save_file_output(result, output_path)
            return None
        else:
            return result  # type: ignore[no-any-return]

    def add_page(
        self,
        input_file: FileInput,
        insert_index: int,
        page_count: int = 1,
        page_size: str = "A4",
        orientation: str = "portrait",
        output_path: str | None = None,
    ) -> bytes | None:
        """Add blank pages to a PDF document.

        Inserts blank pages at the specified insertion index in the document.

        Args:
            input_file: Input PDF file.
            insert_index: Position to insert pages (0-based insertion index).
                         0 = insert before first page (at beginning)
                         1 = insert before second page (after first page)
                         -1 = insert after last page (at end)
            page_count: Number of blank pages to add (default: 1).
            page_size: Page size for new pages. Common values: "A4", "Letter",
                      "Legal", "A3", "A5" (default: "A4").
            orientation: Page orientation. Either "portrait" or "landscape"
                        (default: "portrait").
            output_path: Optional path to save the output file.

        Returns:
            Processed PDF as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
            ValueError: If page_count is less than 1 or if insert_index is
                       a negative number other than -1.

        Examples:
            # Add a single blank page at the beginning
            result = client.add_page("document.pdf", insert_index=0)

            # Add multiple pages at the end
            result = client.add_page(
                "document.pdf",
                insert_index=-1,  # Insert at end
                page_count=3,
                page_size="Letter",
                orientation="landscape"
            )

            # Add pages before third page and save to file
            client.add_page(
                "document.pdf",
                insert_index=2,  # Insert before third page
                page_count=2,
                output_path="with_blank_pages.pdf"
            )
        """
        from nutrient_dws.file_handler import (
            get_pdf_page_count,
            prepare_file_for_upload,
            save_file_output,
        )

        # Validate inputs
        if page_count < 1:
            raise ValueError("page_count must be at least 1")
        if page_count > 100:
            raise ValueError("page_count cannot exceed 100 pages")
        if insert_index < -1:
            raise ValueError("insert_index must be -1 (for end) or a non-negative insertion index")

        # Get total number of pages to validate insert_index
        if insert_index >= 0:  # Skip validation for -1 (end)
            num_of_pages = get_pdf_page_count(input_file)
            if insert_index > num_of_pages:
                raise ValueError(f"insert_index {insert_index} is out of bounds (0-{num_of_pages})")

        # Prepare file for upload
        file_field, file_data = prepare_file_for_upload(input_file, "file")
        files = {file_field: file_data}

        # Build parts array
        parts: list[dict[str, Any]] = []

        # Create new page part
        new_page_part = {
            "page": "new",
            "pageCount": page_count,
            "layout": {
                "size": page_size,
                "orientation": orientation,
            },
        }

        if insert_index == -1:
            # Insert at end: add all original pages first, then new pages
            parts.append({"file": "file"})
            parts.append(new_page_part)
        elif insert_index == 0:
            # Insert at beginning: add new pages first, then all original pages
            parts.append(new_page_part)
            parts.append({"file": "file"})
        else:
            # Insert at specific position: split original document
            # Add pages from start up to insertion point (0 to insert_index-1)
            parts.append({"file": "file", "pages": {"start": 0, "end": insert_index - 1}})

            # Add new blank pages
            parts.append(new_page_part)

            # Add remaining pages from insertion point to end
            parts.append({"file": "file", "pages": {"start": insert_index}})

        # Build instructions for adding pages
        instructions = {"parts": parts, "actions": []}

        # Make API request
        # Type checking: at runtime, self is NutrientClient which has _http_client
        result = self._http_client.post(  # type: ignore[attr-defined]
            "/build",
            files=files,
            json_data=instructions,
        )

        # Handle output
        if output_path:
            save_file_output(result, output_path)
            return None
        else:
            return result  # type: ignore[no-any-return]

    def apply_instant_json(
        self,
        input_file: FileInput,
        instant_json: FileInput | str,
        output_path: str | None = None,
    ) -> bytes | None:
        """Apply Nutrient Instant JSON annotations to a PDF.

        Applies annotations from a Nutrient Instant JSON file or URL to a PDF.
        This allows importing annotations exported from Nutrient SDK or other
        compatible sources.

        Args:
            input_file: Input PDF file.
            instant_json: Instant JSON data as file path, bytes, file object, or URL.
            output_path: Optional path to save the output file.

        Returns:
            PDF with applied annotations as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.

        Example:
            # Apply annotations from file
            client.apply_instant_json(
                "document.pdf",
                "annotations.json",
                output_path="annotated.pdf"
            )

            # Apply annotations from URL
            client.apply_instant_json(
                "document.pdf",
                "https://example.com/annotations.json",
                output_path="annotated.pdf"
            )
        """
        from nutrient_dws.file_handler import prepare_file_for_upload, save_file_output

        # Check if instant_json is a URL
        if isinstance(instant_json, str) and (
            instant_json.startswith("http://") or instant_json.startswith("https://")
        ):
            # Use URL approach
            action = {
                "type": "applyInstantJson",
                "file": {"url": instant_json},
            }

            # Prepare the PDF file
            files = {}
            file_field, file_data = prepare_file_for_upload(input_file, "file")
            files[file_field] = file_data

            instructions = {"parts": [{"file": file_field}], "actions": [action]}
        else:
            # It's a file input - need to upload both files
            files = {}

            # Main PDF file
            file_field, file_data = prepare_file_for_upload(input_file, "file")
            files[file_field] = file_data

            # Instant JSON file
            json_field, json_data = prepare_file_for_upload(instant_json, "instant_json")
            files[json_field] = json_data

            # Build instructions with applyInstantJson action
            action = {
                "type": "applyInstantJson",
                "file": json_field,  # Reference to the uploaded file
            }

            instructions = {"parts": [{"file": file_field}], "actions": [action]}

        # Make API request
        # Type checking: at runtime, self is NutrientClient which has _http_client
        result = self._http_client.post(  # type: ignore[attr-defined]
            "/build",
            files=files,
            json_data=instructions,
        )

        # Handle output
        if output_path:
            save_file_output(result, output_path)
            return None
        else:
            return result  # type: ignore[no-any-return]

    def apply_xfdf(
        self,
        input_file: FileInput,
        xfdf: FileInput | str,
        output_path: str | None = None,
    ) -> bytes | None:
        """Apply XFDF annotations to a PDF.

        Applies annotations from an XFDF (XML Forms Data Format) file or URL
        to a PDF. XFDF is a standard format for exchanging PDF annotations.

        Args:
            input_file: Input PDF file.
            xfdf: XFDF data as file path, bytes, file object, or URL.
            output_path: Optional path to save the output file.

        Returns:
            PDF with applied annotations as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.

        Example:
            # Apply annotations from file
            client.apply_xfdf(
                "document.pdf",
                "annotations.xfdf",
                output_path="annotated.pdf"
            )

            # Apply annotations from URL
            client.apply_xfdf(
                "document.pdf",
                "https://example.com/annotations.xfdf",
                output_path="annotated.pdf"
            )
        """
        from nutrient_dws.file_handler import prepare_file_for_upload, save_file_output

        # Check if xfdf is a URL
        if isinstance(xfdf, str) and (xfdf.startswith("http://") or xfdf.startswith("https://")):
            # Use URL approach
            action = {
                "type": "applyXfdf",
                "file": {"url": xfdf},
            }

            # Prepare the PDF file
            files = {}
            file_field, file_data = prepare_file_for_upload(input_file, "file")
            files[file_field] = file_data

            instructions = {"parts": [{"file": file_field}], "actions": [action]}
        else:
            # It's a file input - need to upload both files
            files = {}

            # Main PDF file
            file_field, file_data = prepare_file_for_upload(input_file, "file")
            files[file_field] = file_data

            # XFDF file
            xfdf_field, xfdf_data = prepare_file_for_upload(xfdf, "xfdf")
            files[xfdf_field] = xfdf_data

            # Build instructions with applyXfdf action
            action = {
                "type": "applyXfdf",
                "file": xfdf_field,  # Reference to the uploaded file
            }

            instructions = {"parts": [{"file": file_field}], "actions": [action]}

        # Make API request
        # Type checking: at runtime, self is NutrientClient which has _http_client
        result = self._http_client.post(  # type: ignore[attr-defined]
            "/build",
            files=files,
            json_data=instructions,
        )

        # Handle output
        if output_path:
            save_file_output(result, output_path)
            return None
        else:
            return result  # type: ignore[no-any-return]

    def set_page_label(
        self,
        input_file: FileInput,
        labels: list[dict[str, Any]],
        output_path: str | None = None,
    ) -> bytes | None:
        """Set labels for specific pages in a PDF.

        Assigns custom labels/numbering to specific page ranges in a PDF document.
        Each label configuration specifies a page range and the label text to apply.

        Args:
            input_file: Input PDF file.
            labels: List of label configurations. Each dict must contain:
                   - 'pages': Page range dict with 'start' (required) and optionally 'end'
                   - 'label': String label to apply to those pages
                   Page ranges use 0-based indexing where 'end' is inclusive.
            output_path: Optional path to save the output file.

        Returns:
            Processed PDF as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
            ValueError: If labels list is empty or contains invalid configurations.

        Examples:
            # Set labels for different page ranges
            client.set_page_label(
                "document.pdf",
                labels=[
                    {"pages": {"start": 0, "end": 2}, "label": "Introduction"},
                    {"pages": {"start": 3, "end": 9}, "label": "Chapter 1"},
                    {"pages": {"start": 10}, "label": "Appendix"}
                ],
                output_path="labeled_document.pdf"
            )

            # Set label for single page
            client.set_page_label(
                "document.pdf",
                labels=[{"pages": {"start": 0, "end": 0}, "label": "Cover Page"}]
            )
        """
        from nutrient_dws.file_handler import (
            get_pdf_page_count,
            prepare_file_for_upload,
            save_file_output,
        )

        # Validate inputs
        if not labels:
            raise ValueError("labels list cannot be empty")

        # Get total number of pages to validate ranges
        num_of_pages = get_pdf_page_count(input_file)

        # Normalize labels to ensure proper format
        normalized_labels = []
        for i, label_config in enumerate(labels):
            if not isinstance(label_config, dict):
                raise ValueError(f"Label configuration {i} must be a dictionary")

            if "pages" not in label_config:
                raise ValueError(f"Label configuration {i} missing required 'pages' key")

            if "label" not in label_config:
                raise ValueError(f"Label configuration {i} missing required 'label' key")

            pages = label_config["pages"]
            if not isinstance(pages, dict) or "start" not in pages:
                raise ValueError(f"Label configuration {i} 'pages' must be a dict with 'start' key")

            # Validate start is within document bounds
            start = pages["start"]
            if start < 0 or start >= num_of_pages:
                raise ValueError(
                    f"Label configuration {i}: start index {start}"
                    f" is out of bounds (0-{num_of_pages - 1})"
                )

            # Normalize pages - only include 'end' if explicitly provided
            normalized_pages = {"start": start}
            if "end" in pages:
                end = pages["end"]
                # Validate end is within document bounds
                if end < 0 or end >= num_of_pages:
                    raise ValueError(
                        f"Label configuration {i}: end index {end}"
                        f" is out of bounds (0-{num_of_pages - 1})"
                    )
                # Validate end is not less than start
                if end < start:
                    raise ValueError(
                        f"Label configuration {i}: end index {end}"
                        f" cannot be less than start index {start}"
                    )
                normalized_pages["end"] = end
            # If no end is specified, leave it out (meaning "to end of document")

            normalized_labels.append({"pages": normalized_pages, "label": label_config["label"]})

        # Prepare file for upload
        file_field, file_data = prepare_file_for_upload(input_file, "file")
        files = {file_field: file_data}

        # Build instructions with page labels in output configuration
        instructions = {
            "parts": [{"file": "file"}],
            "actions": [],
            "output": {"labels": normalized_labels},
        }

        # Make API request
        # Type checking: at runtime, self is NutrientClient which has _http_client
        result = self._http_client.post(  # type: ignore[attr-defined]
            "/build",
            files=files,
            json_data=instructions,
        )

        # Handle output
        if output_path:
            save_file_output(result, output_path)
            return None
        else:
            return result  # type: ignore[no-any-return]
