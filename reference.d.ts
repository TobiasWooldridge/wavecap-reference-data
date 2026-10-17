/** MIT-licensed interface; data remains separately licensed. */
export interface StationReference {
  id: string;
  service: 'SACFS' | 'SAMFS';
  station_code: string;
  facility_name: string;
  station_number: string | null;
  name: string;
  source_url: string;
  listed_in_current_station_index: boolean;
  listed_in_appliance_index: boolean;
  record_kind: 'station_or_group_or_region';
  operational_status: 'unknown';
}
export interface ApplianceReference {
  id: string;
  station_id: string;
  service: 'SACFS' | 'SAMFS';
  full_label: string;
  compact_label: string;
  vehicle_code: string | null;
  vehicle_role: string;
  listing_key: string;
  id_stability: 'registration-aware-listing' | 'provisional';
  source_conflicts?: Record<string, unknown[]>;
  name: string;
  registration: string | null;
  source_updated_text: string | null;
  make_model: string | null;
  class_id: string;
  class_source_url: string;
  source_url: string;
  operational_status: 'listed_at_source';
  water_litres: number | null;
  foam_litres: number | null;
  /** See RIGHTS.md (photo decision 2026-10-17); `credit` is the caption's own credit. */
  photo:
    | { page_url: string; credit: string | null; rights_status: 'cc-by-sa-4.0-sidebar';
        redistribution_allowed: true; image_url: string; license: 'CC-BY-SA-4.0' }
    | { page_url: string; credit: null; rights_status: 'no-photo';
        redistribution_allowed: null; image_url: null; license: null };
};
}
export interface SourceReference {
  url: string;
  sha256: string;
  retrieved_at: string;
  rights_status: 'conflicting-notices';
  attribution: string;
}
export interface ClassReference {
  id: string;
  name: string;
  water_litres_typical: number;
  drive?: string;
  variants?: string[];
  source_type_codes?: string[];
  source_url: string;
  equipment_varies_by_appliance: boolean;
}
export interface ReferenceSnapshot {
  schema_version: 1;
  data_license: 'CC-BY-SA-4.0';
  third_party_rights: string;
  stations: StationReference[];
  appliances: ApplianceReference[];
  classes: ClassReference[];
  sources: SourceReference[];
  coverage: {
    current_station_index_count: number;
    appliance_index_count: number;
    detail_pages_visited: string[];
    detail_page_failures: {station_id: string; error: string}[];
    complete_appliance_inventory: boolean;
    by_service: Record<string, {current_station_index_count: number; appliance_index_count: number; detail_pages_visited: string[]; detail_page_failures: {station_id: string; error: string}[]; complete_appliance_inventory: boolean}>;
  };
}
