/** React Query wrapper for campaign CRUD endpoints. */

import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";
import { useCampaignStore } from "@/store/campaignStore";
import type { Campaign } from "@/types/api";

export function useCampaigns() {
  const setCampaigns = useCampaignStore((s) => s.setCampaigns);

  return useQuery({
    queryKey: ["campaigns"],
    queryFn: async () => {
      const { data } = await api.get<Campaign[]>("/campaigns/");
      const campaigns = Array.isArray(data) ? data : (data as { results?: Campaign[] }).results ?? [];
      setCampaigns(campaigns);
      return campaigns;
    },
  });
}
