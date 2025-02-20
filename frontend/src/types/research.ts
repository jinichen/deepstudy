export interface ResearchRequest {
  topic: string;
  depth: number;
  language: string;
  focus_areas: string[];
}

export interface Reference {
  title: string;
  url: string;
  credibility?: number;
  type?: string;
}

export interface ResearchResponse {
  detailed_analysis: {
    full_report: string;
  };
  conclusions?: string[];
  references?: Reference[];
}