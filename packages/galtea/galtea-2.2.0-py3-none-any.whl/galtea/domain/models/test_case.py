from typing import Optional

from ...utils.from_camel_case_base_model import FromCamelCaseBaseModel


class TestCaseBase(FromCamelCaseBaseModel):
    test_id: str
    input: str
    expected_output: Optional[str] = None
    context: Optional[str] = None
    source: Optional[str] = None
    strategy: Optional[str] = None
    variant: Optional[str] = None


class TestCase(TestCaseBase):
    id: str
    created_at: str
    deleted_at: Optional[str] = None
