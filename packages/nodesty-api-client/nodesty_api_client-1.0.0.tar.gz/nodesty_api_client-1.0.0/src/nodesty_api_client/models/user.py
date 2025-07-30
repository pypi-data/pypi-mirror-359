from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Addon(BaseModel):
    name: str
    recurring_amount: float
    billing_cycle: str
    status: str
    register_date: int
    next_due_date: int


class BillingCycle(str, Enum):
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    SEMI_ANNUALLY = "Semi-Annually"
    ANNUALLY = "Annually"
    BIENNIAL = "Biennial"
    TRIENNIAL = "Triennial"


class Service(BaseModel):
    id: int
    product_id: Optional[int] = Field(alias="productId")
    group_id: Optional[int] = Field(alias="groupId")
    name: str
    raw_name: str = Field(alias="rawName")
    domain: str
    first_payment_amount: float = Field(alias="firstPaymentAmount")
    recurring_amount: float = Field(alias="recurringAmount")
    billing_cycle: BillingCycle = Field(alias="billingCycle")
    next_due_date: int = Field(alias="nextDueDate")
    status: str
    username: str
    password: Optional[str] = None
    vps_id: Optional[int] = Field(alias="vpsId", default=None)
    dedicated_id: Optional[List[str]] = Field(alias="dedicatedId", default=None)
    is_vps: bool = Field(alias="isVps")
    is_web_hosting: bool = Field(alias="isWebHosting")
    is_dedicated: bool = Field(alias="isDedicated")
    is_hetzner_dedicated: bool = Field(alias="isHetznerDedicated")
    is_sky_link_dedicated: bool = Field(alias="isSkyLinkDedicated")
    addons: List[Addon]
    features: List[str]


class TicketStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class TicketPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class TicketAuthorRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class TicketAuthor(BaseModel):
    id: str
    avatar: Optional[str] = None
    name: str
    role: TicketAuthorRole


class TicketMessage(BaseModel):
    id: str
    message_id: str = Field(alias="messageId")
    content: str
    attachments: List[str]
    author_id: str = Field(alias="authorId")
    created_at: str = Field(alias="createdAt")
    author: TicketAuthor


class Ticket(BaseModel):
    id: str
    subject: str
    status: TicketStatus
    priority: TicketPriority
    last_reply: str = Field(alias="lastReply")
    marked: bool = Field(default=False)
    messages: List[TicketMessage]


class UserStats(BaseModel):
    active_services: int = Field(alias="activeServices")
    unpaid_invoices: int = Field(alias="unpaidInvoices")
    balance: float
    active_tickets: int = Field(alias="activeTickets")


class User(BaseModel):
    id: str
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    full_name: str = Field(alias="fullName")
    email: str
    country: str
    city: str
    state: str
    address: str
    post_code: str = Field(alias="postCode")
    currency: str
    currency_symbol: str = Field(alias="currencySymbol")
    phone_number: str = Field(alias="phoneNumber")
    tckn: Optional[str] = None
    birth_year: Optional[str] = Field(alias="birthYear")
    banned: bool
    current_session_id: str = Field(alias="currentSessionId")
    totp_enabled: bool = Field(alias="totpEnabled")
    stats: UserStats
    company_name: Optional[str] = Field(alias="companyName", default=None)


class InvoiceStatus(str, Enum):
    DRAFT = "Draft"
    PAID = "Paid"
    UNPAID = "Unpaid"
    OVERDUE = "Overdue"
    CANCELLED = "Cancelled"
    REFUNDED = "Refunded"
    PAYMENT_PENDING = "Payment Pending"


class InvoiceItem(BaseModel):
    id: int
    item_type: str = Field(alias="type")
    description: str
    amount: float


class Invoice(BaseModel):
    id: int
    due_date: int = Field(alias="dueDate")
    date_paid: Optional[int] = Field(alias="datePaid", default=None)
    sub_total: float = Field(alias="subTotal")
    total: float
    status: InvoiceStatus
    applied_balance: float = Field(alias="appliedBalance")
    items: Optional[List[InvoiceItem]]


class SessionOs(str, Enum):
    DESKTOP = "Desktop"
    MOBILE = "Mobile"


class Session(BaseModel):
    id: str
    ip: str
    location: str
    os: SessionOs
    platform: str
    last_seen: str = Field(alias="lastSeen")
