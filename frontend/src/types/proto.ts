// Tipos gerados a partir das definições protobuf

export interface ReadmeProto {
  name: string;
  version: string;
  description: string;
  tags: string[];
  communication_details: CommunicationDetails;
  security_info: SecurityInfo;
  monetization_info: MonetizationInfo;
  licensing_info: LicensingInfo;
}

export interface CommunicationDetails {
  access_interfaces: AccessInterface[];
  default_data_formats: string[];
}

export interface AccessInterface {
  type: 'UNDEFINED' | 'REST' | 'GRAPHQL' | 'GRPC';
  base_url_or_address: string;
  available_methods_or_operations: string[];
}

export interface SecurityInfo {
  encryption_required: boolean;
}

export interface MonetizationInfo {
  model: 'MODEL_TYPE_UNSPECIFIED' | 'FREE' | 'PAID' | 'FREEMIUM';
  price_details: string;
  currency: string;
  pricing_page_url: string;
  commission_enabled: boolean;
  commission_details_url: string;
}

export interface LicensingInfo {
  license_key: string;
  license_url: string;
}

export interface IntentRequest {
  version: string;
  action: string;
  scope: string;
  parameters: Record<string, string>;
  response_format: string;
  auth_info: AuthInfo;
}

export interface IntentResponse {
  request_id: string;
  response: {
    manifest?: ReadmeProto;
    error?: string;
    raw_data?: Uint8Array;
  };
  metadata: ResponseMetadata;
}

export interface AuthInfo {
  token?: string;
  nft_auth?: NFTAuth;
}

export interface NFTAuth {
  contract_address: string;
  token_id: string;
  wallet_address: string;
}

export interface ResponseMetadata {
  source: string;
  timestamp: number;
  ttl: number;
  extra: Record<string, string>;
}