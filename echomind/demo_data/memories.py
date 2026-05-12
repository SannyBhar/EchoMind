"""Synthetic multi-memory demo dataset for EchoMind research evaluation.

All memories are fictional and clearly synthetic. No real participants or
clinical subjects are represented. Data exists solely for in-silico comparison
of cue planning strategies across a varied autobiographical memory corpus.

Dataset design notes:
- Summaries are written with enough sensory/narrative texture to make
  warm vs. neutral cue distinctions non-trivial.
- People names are included so personalized variants have something to
  anchor to beyond the title and summary.
- Four memories intentionally carry two image asset URIs to exercise
  multi-slide rendering paths.
- Categories span at least 9 distinct themes to avoid over-representing
  any single type of autobiographical event.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DemoMemorySpec:
    """Specification for one synthetic demo memory."""

    memory_id: str
    title: str
    summary: str
    people_names: tuple[str, ...]
    place_name: str
    image_asset_uris: tuple[str, ...]
    category: str
    seed: int


DEMO_MEMORIES: tuple[DemoMemorySpec, ...] = (
    DemoMemorySpec(
        memory_id="demo-university-001",
        title="First Day at University",
        summary=(
            "Walked across the main quad with a hand-drawn map, found the right"
            " lecture building ten minutes late, and slid into a seat next to someone"
            " who turned out to know the layout — the first conversation of a long friendship."
        ),
        people_names=("Asha Patel", "Professor Lin"),
        place_name="New Brunswick Campus",
        image_asset_uris=(
            "s3://demo-assets/campus-path.jpg",
            "s3://demo-assets/campus-lecture-hall.jpg",
        ),
        category="university",
        seed=7,
    ),
    DemoMemorySpec(
        memory_id="demo-graduation-001",
        title="Graduation Ceremony",
        summary=(
            "Stood in a slow-moving line in rented robes, heard the name announced"
            " over a PA that echoed too much, and walked across a stage that felt"
            " smaller than expected — then found Maria and James in the crowd afterwards."
        ),
        people_names=("Maria Santos", "James Okonkwo"),
        place_name="Convention Center Auditorium",
        image_asset_uris=(
            "s3://demo-assets/graduation-stage.jpg",
            "s3://demo-assets/diploma-closeup.jpg",
        ),
        category="achievement",
        seed=42,
    ),
    DemoMemorySpec(
        memory_id="demo-road-trip-001",
        title="Summer Road Trip to the Coast",
        summary=(
            "Drove three days along Route 1 with Tyler and Sam, splitting gas and"
            " navigating by instinct after the phone died — stopped at a roadside"
            " diner where the coffee was terrible and the pie was worth the detour."
        ),
        people_names=("Tyler Nguyen", "Sam Rivera"),
        place_name="Pacific Coast Highway",
        image_asset_uris=("s3://demo-assets/coastal-road.jpg",),
        category="travel",
        seed=13,
    ),
    DemoMemorySpec(
        memory_id="demo-first-job-001",
        title="First Day at a New Job",
        summary=(
            "Spent the morning figuring out where things were — the bathroom, the"
            " unwritten seating rules, which coffee machine actually worked."
            " Rachel handed over a stack of onboarding docs; David showed where the"
            " real work happened, which was nothing like the job description."
        ),
        people_names=("Rachel Kim", "David Torres"),
        place_name="Downtown Office Building",
        image_asset_uris=("s3://demo-assets/office-lobby.jpg",),
        category="career",
        seed=21,
    ),
    DemoMemorySpec(
        memory_id="demo-birthday-party-001",
        title="Surprise Birthday Party",
        summary=(
            "Walked into what was supposed to be a quiet dinner and found the whole"
            " extended family packed into the living room. Grandma Rose had organised"
            " it; Uncle Leo had kept the secret badly. Jamie Park caught the expression"
            " on film before anyone else managed to say a word."
        ),
        people_names=("Grandma Rose", "Uncle Leo", "Jamie Park"),
        place_name="Family Home Living Room",
        image_asset_uris=("s3://demo-assets/birthday-party.jpg",),
        category="social",
        seed=55,
    ),
    DemoMemorySpec(
        memory_id="demo-hiking-001",
        title="Sunrise Hike to the Summit",
        summary=(
            "Left the trailhead at 4am with headlamps and a thermos. The climb was"
            " cold and quiet except for Priya's commentary on the stars. At the ridge"
            " the sky went pale, then pink, then suddenly the sun was there — wider"
            " than any horizon seen from a window."
        ),
        people_names=("Priya Sharma",),
        place_name="Blue Ridge Trail Summit",
        image_asset_uris=(
            "s3://demo-assets/mountain-sunrise.jpg",
            "s3://demo-assets/trail-headlamps.jpg",
        ),
        category="adventure",
        seed=88,
    ),
    DemoMemorySpec(
        memory_id="demo-travel-abroad-001",
        title="First Time Traveling Abroad",
        summary=(
            "Cleared customs alone in an airport where none of the signs were in English,"
            " found a bus into the old city by following Chloe's texted directions, and"
            " arrived at the hostel Marco had booked — a room above a bakery that smelled"
            " of anise and bread at every hour."
        ),
        people_names=("Chloe Dubois", "Marco Bianchi"),
        place_name="Barcelona Airport and Gothic Quarter",
        image_asset_uris=(
            "s3://demo-assets/barcelona-street.jpg",
            "s3://demo-assets/hostel-entrance.jpg",
        ),
        category="travel",
        seed=33,
    ),
    DemoMemorySpec(
        memory_id="demo-family-holiday-001",
        title="Family Holiday Dinner",
        summary=(
            "Sat around the big farmhouse table that Grandpa Joe had built in the"
            " seventies — the same dishes, the same argument about whether the gravy"
            " needed more thyme, Aunt Clara's story about the year the turkey burned."
            " Cousin Ben arrived late, as always, and the meal got louder."
        ),
        people_names=("Grandpa Joe", "Aunt Clara", "Cousin Ben"),
        place_name="Grandparents' Farmhouse Kitchen",
        image_asset_uris=("s3://demo-assets/holiday-dinner.jpg",),
        category="family",
        seed=77,
    ),
    DemoMemorySpec(
        memory_id="demo-cooking-001",
        title="Learning to Make Pasta from Scratch",
        summary=(
            "Nonna Lucia's kitchen was warm and smelled of semolina. The first two"
            " attempts tore when rolled too thin; the third held. She said nothing,"
            " just handed over the cutter — a sign that the lesson was over and the"
            " real thing could begin."
        ),
        people_names=("Nonna Lucia",),
        place_name="Cooking Studio",
        image_asset_uris=("s3://demo-assets/pasta-making.jpg",),
        category="skill",
        seed=19,
    ),
    DemoMemorySpec(
        memory_id="demo-school-reunion-001",
        title="High School Reunion",
        summary=(
            "The gymnasium still smelled the same. Chris Hoffman looked exactly like"
            " his yearbook photo. Dana Lee did not. Pat Sullivan had driven six hours"
            " and seemed the most at ease of anyone there. An hour stretched into three"
            " — the awkwardness dissolved faster than expected."
        ),
        people_names=("Chris Hoffman", "Dana Lee", "Pat Sullivan"),
        place_name="Westview High School Gymnasium",
        image_asset_uris=("s3://demo-assets/reunion-gym.jpg",),
        category="social",
        seed=64,
    ),
    DemoMemorySpec(
        memory_id="demo-first-apartment-001",
        title="Moving Into First Apartment",
        summary=(
            "Alex Chen showed up with a truck and strong opinions about furniture layout."
            " By 9pm the bed was assembled with one bolt missing, the boxes were stacked"
            " in what would become the living room, and the two of them were eating"
            " noodles on the floor because there were no chairs yet."
        ),
        people_names=("Alex Chen",),
        place_name="Third-Floor Walkup Apartment",
        image_asset_uris=("s3://demo-assets/empty-apartment.jpg",),
        category="life_event",
        seed=44,
    ),
    DemoMemorySpec(
        memory_id="demo-late-drive-001",
        title="Driving Home After the Last Day at an Old Job",
        summary=(
            "Took the long route home after clearing out the desk for the last time."
            " The box of things sat in the passenger seat. Elena Vasquez had called"
            " somewhere around exit 14; the conversation lasted until the highway"
            " gave way to surface streets, and something shifted by the time the key"
            " was in the door."
        ),
        people_names=("Elena Vasquez",),
        place_name="Interstate Highway at Night",
        image_asset_uris=("s3://demo-assets/night-highway.jpg",),
        category="transition",
        seed=37,
    ),
)

DEMO_MEMORY_CATEGORIES: frozenset[str] = frozenset(m.category for m in DEMO_MEMORIES)
