# Frontend Test Plan

## 1. Ingestion
- Verify PDF and DOCX uploads are accepted.
- Reject unsupported files such as `.txt`.
- Confirm the 10 MB size limit is enforced before submission.

## 2. Model Response
- Ensure risk levels render correctly from the API payload.
- Validate the score, level, and reasons list all populate.

## 3. Search
- Check that search input is present and usable for clause/entity lookup.

## 4. UI
- Verify dashboard sections render in the expected order.
- Ensure each important control has an accessible label.

## 5. Security
- Confirm client-side validation blocks invalid extensions and oversized files.
- Check that API requests use the configured base URL.

## 6. Release
- Run all frontend unit tests before demo release.
- Capture verification screenshots for upload and results states.
