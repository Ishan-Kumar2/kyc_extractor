"""
Validation and sanity check tests for extracted KYC document data.
Runs after extraction to verify data integrity and catch obvious errors.
"""

from typing import Dict, Any, List, Tuple
from datetime import datetime
import re


class ValidationResult:
    """Result of a validation test."""

    def __init__(
        self, test_name: str, passed: bool, message: str, severity: str = "error"
    ):
        """
        Args:
            test_name: Name of the validation test
            passed: Whether the test passed
            message: Description of the result
            severity: "error" for critical issues, "warning" for minor issues
        """
        self.test_name = test_name
        self.passed = passed
        self.message = message
        self.severity = severity

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "test": self.test_name,
            "passed": self.passed,
            "message": self.message,
            "severity": self.severity,
        }


class DocumentValidator:
    """Validator for KYC document extraction results."""

    # Valid ISO 3166 country codes and common variations
    VALID_COUNTRIES = {
        "USA",
        "US",
        "UNITED STATES",
        "UNITED STATES OF AMERICA",
        "UK",
        "GB",
        "UNITED KINGDOM",
        "GREAT BRITAIN",
        "CANADA",
        "CA",
        "CAN",
        "AUSTRALIA",
        "AU",
        "AUS",
        "INDIA",
        "IN",
        "IND",
        "CHINA",
        "CN",
        "CHN",
        "JAPAN",
        "JP",
        "JPN",
        "GERMANY",
        "DE",
        "DEU",
        "FRANCE",
        "FR",
        "FRA",
        "ITALY",
        "IT",
        "ITA",
        "SPAIN",
        "ES",
        "ESP",
        "MEXICO",
        "MX",
        "MEX",
        "BRAZIL",
        "BR",
        "BRA",
        "RUSSIA",
        "RU",
        "RUS",
        "SOUTH AFRICA",
        "ZA",
        "ZAF",
        # Add more as needed
    }

    # Valid US states
    US_STATES = {
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
        "ALABAMA",
        "ALASKA",
        "ARIZONA",
        "ARKANSAS",
        "CALIFORNIA",
        "COLORADO",
        "CONNECTICUT",
        "DELAWARE",
        "FLORIDA",
        "GEORGIA",
        "HAWAII",
        "IDAHO",
        "ILLINOIS",
        "INDIANA",
        "IOWA",
        "KANSAS",
        "KENTUCKY",
        "LOUISIANA",
        "MAINE",
        "MARYLAND",
        "MASSACHUSETTS",
        "MICHIGAN",
        "MINNESOTA",
        "MISSISSIPPI",
        "MISSOURI",
        "MONTANA",
        "NEBRASKA",
        "NEVADA",
        "NEW HAMPSHIRE",
        "NEW JERSEY",
        "NEW MEXICO",
        "NEW YORK",
        "NORTH CAROLINA",
        "NORTH DAKOTA",
        "OHIO",
        "OKLAHOMA",
        "OREGON",
        "PENNSYLVANIA",
        "RHODE ISLAND",
        "SOUTH CAROLINA",
        "SOUTH DAKOTA",
        "TENNESSEE",
        "TEXAS",
        "UTAH",
        "VERMONT",
        "VIRGINIA",
        "WASHINGTON",
        "WEST VIRGINIA",
        "WISCONSIN",
        "WYOMING",
    }

    def __init__(self):
        self.results: List[ValidationResult] = []

    def validate(self, extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run all validation tests on extraction result.

        Args:
            extraction_result: The result from document extraction

        Returns:
            Dictionary with validation results and summary
        """
        self.results = []

        if extraction_result.get("status") != "success":
            return {
                "validation_run": False,
                "message": "Validation skipped - extraction was not successful",
            }

        doc_type = extraction_result.get("document_type")
        essential_fields = extraction_result.get("essential_fields", {})
        metadata = extraction_result.get("metadata", {})

        # Run common validation tests
        self._validate_essential_fields(essential_fields)

        # Run document-specific tests
        if doc_type == "passport":
            self._validate_passport(essential_fields, metadata)
        elif doc_type == "drivers_license":
            self._validate_license(essential_fields, metadata)
        elif doc_type == "other_id":
            self._validate_other_id(essential_fields, metadata)

        # Compile results
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = sum(1 for r in self.results if not r.passed)
        errors = [r for r in self.results if not r.passed and r.severity == "error"]
        warnings = [r for r in self.results if not r.passed and r.severity == "warning"]

        return {
            "validation_run": True,
            "total_tests": len(self.results),
            "passed": passed_tests,
            "failed": failed_tests,
            "errors": len(errors),
            "warnings": len(warnings),
            "all_tests_passed": failed_tests == 0,
            "test_results": [r.to_dict() for r in self.results],
            "error_details": [r.to_dict() for r in errors],
            "warning_details": [r.to_dict() for r in warnings],
        }

    def _add_result(
        self, test_name: str, passed: bool, message: str, severity: str = "error"
    ):
        """Add a validation result."""
        self.results.append(ValidationResult(test_name, passed, message, severity))

    def _validate_essential_fields(self, essential_fields: Dict[str, Any]):
        """Validate common essential fields across all document types."""

        # Test: Full name should be present and non-empty
        full_name = essential_fields.get("full_name", {}).get("value", "").strip()
        if full_name:
            self._add_result(
                "essential_fields.full_name.present",
                True,
                f"Full name is present: {full_name}",
            )

            # Test: Name should have at least 2 parts (first and last)
            name_parts = full_name.split()
            if len(name_parts) >= 2:
                self._add_result(
                    "essential_fields.full_name.format",
                    True,
                    "Name has at least first and last name",
                )
            else:
                self._add_result(
                    "essential_fields.full_name.format",
                    False,
                    f"Name may be incomplete - only {len(name_parts)} part(s) found",
                    "warning",
                )
        else:
            self._add_result(
                "essential_fields.full_name.present",
                False,
                "Full name is missing or empty",
            )

        # Test: Date of birth validation
        dob = essential_fields.get("date_of_birth", {}).get("value", "")
        if dob:
            dob_valid, dob_date = self._validate_date(dob)
            if dob_valid:
                self._add_result(
                    "essential_fields.date_of_birth.format",
                    True,
                    f"Date of birth is in valid format: {dob}",
                )

                # Test: DOB should be in the past
                if dob_date < datetime.now():
                    self._add_result(
                        "essential_fields.date_of_birth.past",
                        True,
                        "Date of birth is in the past",
                    )
                else:
                    self._add_result(
                        "essential_fields.date_of_birth.past",
                        False,
                        "Date of birth is in the future - invalid",
                    )

                # Test: Person should be at least 1 year old and less than 150 years old
                age = (datetime.now() - dob_date).days / 365.25
                if 1 <= age <= 150:
                    self._add_result(
                        "essential_fields.date_of_birth.reasonable",
                        True,
                        f"Age is reasonable: ~{int(age)} years",
                    )
                else:
                    self._add_result(
                        "essential_fields.date_of_birth.reasonable",
                        False,
                        f"Age seems unreasonable: ~{int(age)} years",
                    )
            else:
                self._add_result(
                    "essential_fields.date_of_birth.format",
                    False,
                    f"Date of birth format is invalid: {dob}",
                )
        else:
            self._add_result(
                "essential_fields.date_of_birth.present",
                False,
                "Date of birth is missing",
            )

        # Test: Sex validation
        sex = essential_fields.get("sex", {}).get("value", "")
        if sex in ["M", "F", "X"]:
            self._add_result("essential_fields.sex.valid", True, f"Sex is valid: {sex}")
        elif sex:
            self._add_result(
                "essential_fields.sex.valid",
                False,
                f"Sex value is invalid: {sex} (expected M, F, or X)",
                "warning",
            )
        else:
            self._add_result(
                "essential_fields.sex.present", False, "Sex is missing", "warning"
            )

    def _validate_passport(
        self, essential_fields: Dict[str, Any], metadata: Dict[str, Any]
    ):
        """Validate passport-specific fields."""

        # Test: Passport number should be present and typically 6-9 alphanumeric characters
        passport_num = metadata.get("passport_number", {}).get("value", "")
        if passport_num:
            # Remove spaces and special characters
            clean_num = re.sub(r"[^A-Z0-9]", "", passport_num.upper())
            if 6 <= len(clean_num) <= 15:
                self._add_result(
                    "passport.passport_number.length",
                    True,
                    f"Passport number length is valid: {len(clean_num)} characters",
                )
            else:
                self._add_result(
                    "passport.passport_number.length",
                    False,
                    f"Passport number length is unusual: {len(clean_num)} characters (expected 6-15)",
                    "warning",
                )
        else:
            self._add_result(
                "passport.passport_number.present", False, "Passport number is missing"
            )

        # Test: Country of issue should be valid
        country = metadata.get("country_of_issue", {}).get("value", "")
        if country:
            if country.upper() in self.VALID_COUNTRIES:
                self._add_result(
                    "passport.country_of_issue.valid",
                    True,
                    f"Country of issue is valid: {country}",
                )
            else:
                self._add_result(
                    "passport.country_of_issue.valid",
                    False,
                    f"Country of issue may be invalid or unrecognized: {country}",
                    "warning",
                )
        else:
            self._add_result(
                "passport.country_of_issue.present",
                False,
                "Country of issue is missing",
            )

        # Test: Nationality should be valid
        nationality = metadata.get("nationality", {}).get("value", "")
        if nationality:
            if nationality.upper() in self.VALID_COUNTRIES:
                self._add_result(
                    "passport.nationality.valid",
                    True,
                    f"Nationality is valid: {nationality}",
                )
            else:
                self._add_result(
                    "passport.nationality.valid",
                    False,
                    f"Nationality may be invalid or unrecognized: {nationality}",
                    "warning",
                )

        # Test: Date validations
        self._validate_document_dates(
            metadata.get("date_of_issue", {}).get("value"),
            metadata.get("date_of_expiry", {}).get("value"),
            essential_fields.get("date_of_birth", {}).get("value"),
            "passport",
        )

    def _validate_license(
        self, essential_fields: Dict[str, Any], metadata: Dict[str, Any]
    ):
        """Validate driver's license-specific fields."""

        # Test: DL number should be present
        dl_number = metadata.get("dl_number", {}).get("value", "")
        if dl_number:
            clean_num = re.sub(r"[^A-Z0-9]", "", dl_number.upper())
            if 5 <= len(clean_num) <= 20:
                self._add_result(
                    "license.dl_number.length",
                    True,
                    f"License number length is valid: {len(clean_num)} characters",
                )
            else:
                self._add_result(
                    "license.dl_number.length",
                    False,
                    f"License number length is unusual: {len(clean_num)} characters",
                    "warning",
                )
        else:
            self._add_result(
                "license.dl_number.present", False, "License number is missing"
            )

        # Test: Address should be present for licenses (required field)
        address = essential_fields.get("address", {}).get("value", "")
        if address and len(address.strip()) > 5:
            self._add_result(
                "license.address.present",
                True,
                "Address is present and appears complete",
            )
        else:
            self._add_result(
                "license.address.present", False, "Address is missing or incomplete"
            )

        # Test: Height format validation
        height = metadata.get("height", {}).get("value", "")
        if height:
            # Check for common height formats
            height_patterns = [
                r"\d+\'\s*\d+\"",  # 5'10"
                r"\d+\s*ft\s*\d*\s*in",  # 5 ft 10 in
                r"\d+\s*cm",  # 170 cm
            ]
            if any(
                re.search(pattern, height, re.IGNORECASE) for pattern in height_patterns
            ):
                self._add_result(
                    "license.height.format", True, f"Height format is valid: {height}"
                )
            else:
                self._add_result(
                    "license.height.format",
                    False,
                    f"Height format may be invalid: {height}",
                    "warning",
                )

        # Test: Weight format validation
        weight = metadata.get("weight", {}).get("value", "")
        if weight:
            # Check for common weight formats
            weight_patterns = [
                r"\d+\s*lbs?",  # 150 lbs
                r"\d+\s*kg",  # 70 kg
            ]
            if any(
                re.search(pattern, weight, re.IGNORECASE) for pattern in weight_patterns
            ):
                self._add_result(
                    "license.weight.format", True, f"Weight format is valid: {weight}"
                )
            else:
                self._add_result(
                    "license.weight.format",
                    False,
                    f"Weight format may be invalid: {weight}",
                    "warning",
                )

        # Test: Date validations
        self._validate_document_dates(
            metadata.get("date_of_issue", {}).get("value"),
            metadata.get("date_of_expiry", {}).get("value"),
            essential_fields.get("date_of_birth", {}).get("value"),
            "license",
        )

    def _validate_other_id(
        self, essential_fields: Dict[str, Any], metadata: Dict[str, Any]
    ):
        """Validate other ID types - more lenient since these vary greatly."""

        # Test: At least some metadata should be present
        if metadata and any(
            v.get("value") for v in metadata.values() if isinstance(v, dict)
        ):
            self._add_result(
                "other_id.metadata.present",
                True,
                "Some metadata fields were successfully extracted",
            )
        else:
            self._add_result(
                "other_id.metadata.present",
                False,
                "No metadata could be extracted from this ID",
                "warning",
            )

        # Test: ID type should ideally be identified
        id_type = metadata.get("id_type", {}).get("value", "")
        if id_type:
            self._add_result(
                "other_id.id_type.identified",
                True,
                f"ID type was identified: {id_type}",
            )
        else:
            self._add_result(
                "other_id.id_type.identified",
                False,
                "ID type could not be identified",
                "warning",
            )

        # Test: Date validations (if dates are present)
        if metadata.get("date_of_issue") or metadata.get("date_of_expiry"):
            self._validate_document_dates(
                metadata.get("date_of_issue", {}).get("value"),
                metadata.get("date_of_expiry", {}).get("value"),
                essential_fields.get("date_of_birth", {}).get("value"),
                "other_id",
            )

    def _validate_document_dates(
        self, issue_date: str, expiry_date: str, dob: str, doc_type: str
    ):
        """Validate date relationships for documents."""

        issue_valid, issue_dt = (
            self._validate_date(issue_date) if issue_date else (False, None)
        )
        expiry_valid, expiry_dt = (
            self._validate_date(expiry_date) if expiry_date else (False, None)
        )
        dob_valid, dob_dt = self._validate_date(dob) if dob else (False, None)

        # Test: Issue date should be valid
        if issue_date:
            if issue_valid:
                self._add_result(
                    f"{doc_type}.date_of_issue.format",
                    True,
                    f"Date of issue is valid: {issue_date}",
                )
            else:
                self._add_result(
                    f"{doc_type}.date_of_issue.format",
                    False,
                    f"Date of issue format is invalid: {issue_date}",
                )

        # Test: Expiry date should be valid
        if expiry_date:
            if expiry_valid:
                self._add_result(
                    f"{doc_type}.date_of_expiry.format",
                    True,
                    f"Date of expiry is valid: {expiry_date}",
                )
            else:
                self._add_result(
                    f"{doc_type}.date_of_expiry.format",
                    False,
                    f"Date of expiry format is invalid: {expiry_date}",
                )

        # Test: Expiry should be after issue
        if issue_valid and expiry_valid:
            if expiry_dt > issue_dt:
                self._add_result(
                    f"{doc_type}.dates.expiry_after_issue",
                    True,
                    "Expiry date is after issue date",
                )
            else:
                self._add_result(
                    f"{doc_type}.dates.expiry_after_issue",
                    False,
                    f"Expiry date ({expiry_date}) is not after issue date ({issue_date})",
                )

        # Test: Issue date should be after DOB
        if issue_valid and dob_valid:
            if issue_dt > dob_dt:
                self._add_result(
                    f"{doc_type}.dates.issue_after_birth",
                    True,
                    "Issue date is after date of birth",
                )
            else:
                self._add_result(
                    f"{doc_type}.dates.issue_after_birth",
                    False,
                    f"Issue date ({issue_date}) is before date of birth ({dob})",
                )

        # Test: Document validity period should be reasonable
        if issue_valid and expiry_valid:
            validity_years = (expiry_dt - issue_dt).days / 365.25
            # Most documents are valid for 1-15 years
            if 0.5 <= validity_years <= 20:
                self._add_result(
                    f"{doc_type}.dates.validity_period",
                    True,
                    f"Document validity period is reasonable: ~{validity_years:.1f} years",
                )
            else:
                self._add_result(
                    f"{doc_type}.dates.validity_period",
                    False,
                    f"Document validity period seems unusual: ~{validity_years:.1f} years",
                    "warning",
                )

        # Test: Check if document is expired
        if expiry_valid:
            if expiry_dt > datetime.now():
                self._add_result(
                    f"{doc_type}.dates.not_expired",
                    True,
                    f"Document is not expired (expires {expiry_date})",
                )
            else:
                self._add_result(
                    f"{doc_type}.dates.not_expired",
                    False,
                    f"Document has expired (expired on {expiry_date})",
                    "warning",
                )

    def _validate_date(self, date_str: str) -> Tuple[bool, datetime]:
        """
        Validate date string in YYYY-MM-DD format.

        Returns:
            Tuple of (is_valid, datetime_object)
        """
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return True, dt
        except (ValueError, TypeError):
            return False, None
