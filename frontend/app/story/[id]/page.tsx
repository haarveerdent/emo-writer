import { getStory, getStories } from "@/lib/supabase";
import { notFound } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, ArrowUp } from "lucide-react";

export const revalidate = 3600;

export async function generateStaticParams() {
  const stories = await getStories(0, 50);
  return stories.map((s) => ({ id: s.id }));
}

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const h = Math.floor(diff / 3600000);
  if (h < 1) return "just now";
  if (h < 24) return `${h}h ago`;
  const d = Math.floor(h / 24);
  return `${d}d ago`;
}

export default async function StoryPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const story = await getStory(id);
  if (!story) notFound();

  const paragraphs = story.content.split(/\n+/).filter(Boolean);

  return (
    <div className="max-w-2xl mx-auto">
      <Link
        href="/"
        className="inline-flex items-center gap-2 text-sm text-neutral-500 hover:text-neutral-300 transition-colors mb-8"
      >
        <ArrowLeft size={14} />
        All stories
      </Link>

      <article>
        <p className="text-xs text-neutral-500 mb-3">
          r/{story.subreddit} · {timeAgo(story.created_at)}
        </p>

        <h1 className="text-2xl font-bold text-neutral-100 leading-snug mb-6">
          {story.title}
        </h1>

        <div className="flex items-center gap-2 mb-8 text-xs text-neutral-600">
          <ArrowUp size={12} />
          <span>{story.upvotes.toLocaleString()} upvotes on Reddit</span>
        </div>

        <div className="prose prose-neutral prose-invert max-w-none">
          {paragraphs.map((p, i) => (
            <p key={i} className="text-neutral-300 leading-relaxed mb-4 text-[15px]">
              {p}
            </p>
          ))}
        </div>
      </article>
    </div>
  );
}
