import Link from "next/link";
import { ArrowUp, MessageCircle } from "lucide-react";
import type { Story } from "@/lib/supabase";

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const h = Math.floor(diff / 3600000);
  if (h < 1) return "just now";
  if (h < 24) return `${h}h ago`;
  const d = Math.floor(h / 24);
  return `${d}d ago`;
}

export default function StoryCard({ story }: { story: Story }) {
  const preview = story.content.slice(0, 200).trimEnd();
  const truncated = story.content.length > 200;

  return (
    <Link href={`/story/${story.id}`}>
      <article className="group border border-neutral-800 rounded-xl p-5 hover:border-neutral-600 hover:bg-neutral-900 transition-all cursor-pointer">
        <div className="flex items-start gap-4">
          <div className="flex-1 min-w-0">
            <p className="text-xs text-neutral-500 mb-2">
              r/{story.subreddit} · {timeAgo(story.created_at)}
            </p>
            <h2 className="font-semibold text-neutral-100 leading-snug mb-3 group-hover:text-white">
              {story.title}
            </h2>
            <p className="text-sm text-neutral-400 leading-relaxed line-clamp-3">
              {preview}{truncated ? "…" : ""}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-4 mt-4 text-xs text-neutral-600">
          <span className="flex items-center gap-1">
            <ArrowUp size={12} />
            {story.upvotes.toLocaleString()}
          </span>
          <span className="text-neutral-700 group-hover:text-neutral-500 transition-colors">
            Read full story →
          </span>
        </div>
      </article>
    </Link>
  );
}
