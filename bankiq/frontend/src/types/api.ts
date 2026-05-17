/** API response types for BankIQ CRM REST endpoints. */

import type { PipelineEventStatus } from "@/types/agent";

export enum KYCStatus {
  Pending = "pending",
  Complete = "complete",
  Failed = "failed",
}

export enum CampaignStatus {
  Draft = "draft",
  Active = "active",
  Completed = "completed",
  Cancelled = "cancelled",
}

export enum DispatchStatus {
  Pending = "pending",
  Approved = "approved",
  Rejected = "rejected",
  Sent = "sent",
  Failed = "failed",
}

export enum HttpHeader {
  Authorization = "Authorization",
  ContentType = "Content-Type",
}

export enum HttpContentType {
  Json = "application/json",
}

export enum HttpStatus {
  Unauthorized = 401,
}

export enum AuthScheme {
  Bearer = "Bearer",
}

export interface RelationshipManager {
  id: string;
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  employee_id: string;
  branch_code: string;
}

export interface Customer {
  id: string;
  name: string;
  phone: string;
  email: string;
  pan: string;
  aadhaar: string;
  account_number: string;
  annual_income: string;
  credit_score: number;
  emi_ratio: string;
  age: number;
  tenure_years: number;
  savings_balance: string;
  last_login: string | null;
  kyc_status: KYCStatus;
  marketing_consent: boolean;
  do_not_contact: boolean;
  has_active_fd: boolean;
  created_at: string;
}

export interface Campaign {
  id: string;
  name: string;
  description: string;
  status: CampaignStatus;
  query_text: string;
  created_at: string;
  updated_at: string;
}

export interface OutreachRecord {
  id: string;
  campaign: string;
  customer: string;
  conversion_score: string | null;
  message_text: string;
  dispatch_status: DispatchStatus;
  rejection_reason: string;
  created_at: string;
}

export interface TokenPair {
  access: string;
  refresh: string;
}

export interface AgentQueryResponse {
  session_id: string;
  status: PipelineEventStatus;
  websocket_url: string;
}
