from enum import StrEnum


class JobAdStatus(StrEnum):
    NOT_APPLIED = "not_applied"
    APPLIED = "applied"
    REJECTED = "rejected"
    ACCEPTED = "accepted"
    ARCHIVED = "archived"


class EmailStatus(StrEnum):
    PENDING = "pending"
    REJECTED = "rejected"
    ACCEPTED = "accepted"
    UNKNOWN = "unknown"


class MatchStatus(StrEnum):
    NOT_SET = "not_set"
    SET = "set"
    NEEDS_REVIEW = "needs_review"


class ApplicationStatus(StrEnum):
    APPLIED = "applied"
    PENDING = "pending"
    REJECTED = "rejected"
    ACCEPTED = "accepted"
    UNKNOWN = "unknown"

