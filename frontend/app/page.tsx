import { getStories } from "@/lib/supabase";
import StoryCard from "@/components/StoryCard";

export const revalidate = 3600; // ISR — revalidate every hour

export default async function HomePage() {
  const stories = await getStories(0, 20);

  return (
    <div>
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-neutral-100">Latest Stories</h2>
        <p className="text-sm text-neutral-500 mt-1">
          {stories.length} stories · updated daily
        </p>
      </div>

      {stories.length === 0 ? (
        <div className="text-center py-20 text-neutral-600">
          No stories yet. Check back soon.
        </div>
      ) : (
        <div className="flex flex-col gap-4">
          {stories.map((story) => (
            <StoryCard key={story.id} story={story} />
          ))}
        </div>
      )}
    </div>
  );
}
