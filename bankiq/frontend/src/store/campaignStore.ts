/** Campaign list and active campaign state. */

import { create } from "zustand";

import type { Campaign, OutreachRecord } from "@/types/api";

interface CampaignStore {
  campaigns: Campaign[];
  activeCampaign: Campaign | null;
  outreachRecords: OutreachRecord[];
  setCampaigns: (campaigns: Campaign[]) => void;
  setActiveCampaign: (campaign: Campaign | null) => void;
  setOutreachRecords: (records: OutreachRecord[]) => void;
}

export const useCampaignStore = create<CampaignStore>((set) => ({
  campaigns: [],
  activeCampaign: null,
  outreachRecords: [],

  setCampaigns: (campaigns) => set({ campaigns }),
  setActiveCampaign: (activeCampaign) => set({ activeCampaign }),
  setOutreachRecords: (outreachRecords) => set({ outreachRecords }),
}));
