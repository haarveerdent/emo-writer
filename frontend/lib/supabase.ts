import { createClient } from "@supabase/supabase-js";

export type Story = {
  id: string;
  reddit_id: string;
  title: string;
  content: string;
  subreddit: string;
  upvotes: number;
  created_at: string;
};

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export async function getStories(page = 0, pageSize = 10): Promise<Story[]> {
  const { data, error } = await supabase
    .from("published_stories")
    .select("*")
    .order("created_at", { ascending: false })
    .range(page * pageSize, (page + 1) * pageSize - 1);

  if (error) throw error;
  return data ?? [];
}

export async function getStory(id: string): Promise<Story | null> {
  const { data, error } = await supabase
    .from("published_stories")
    .select("*")
    .eq("id", id)
    .single();

  if (error) return null;
  return data;
}
