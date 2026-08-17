import omni.replicator.core as rep
from omni.isaac.core.utils.nucleus import get_assets_root_path
# --- CONFIGURATION ---
# IMPORTANT: Update this path to match your local folder structure!
# Use forward slashes (/) even on Windows.
OUTPUT_DIR = "/path_to/issac-data-synth/output"
NUM_FRAMES = 100  # How many images to generate [cite: 11]

# --- HELPER: FIND ASSETS ---
# This finds the NVIDIA Nucleus server automatically
assets_root_path = get_assets_root_path()
if assets_root_path is None:
    print("Error: Could not find NVIDIA Assets. Is Nucleus running?")
    # Fallback paths just in case (Online)
    CARDBOARD_BOX_URL = "http://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/2023.1.1/Isaac/Props/YCB/Axis_Aligned/003_cracker_box.usd"
    WAREHOUSE_URL = "http://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/2023.1.1/Isaac/Environments/Simple_Warehouse/warehouse.usd"
    PALLET_URL = "http://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/ArchVis/Industrial/Pallets/Pallet_B1.usd"
else:
    # Local Paths (Much Faster)
    CARDBOARD_BOX_URL = assets_root_path + "/Isaac/Props/YCB/Axis_Aligned/003_cracker_box.usd"
    WAREHOUSE_URL = assets_root_path + "/Isaac/Environments/Simple_Warehouse/warehouse.usd"
    PALLET_URL = assets_root_path + "/Isaac/Environments/Simple_Warehouse/Props/SM_PaletteA_01.usd"


# --- 1. SCENE SETUP ---
def setup_scene():
    with rep.new_layer():
        # 1. Add a Realistic Warehouse Environment
        # We use 'create.from_usd' to load a full 3D world
        env = rep.create.from_usd(WAREHOUSE_URL)

        # 2. Add the Target Object (Cardboard Box)
        # We make it larger so it's easy to see
        target = rep.create.from_usd(
            CARDBOARD_BOX_URL,
            semantics=[('class', 'industrial_box')],
            position=(0, 2, 0),
            scale=(5, 5, 5)
        )

        # 3. Add Distractors (Clutter)
        # Random pallets in the background to confuse the model (Good for training!)
        distractors = rep.create.from_usd(
            PALLET_URL,
            position=(5, 0, 5),
            count=5  # Create 5 random pallets
        )

        # 4. Camera & Light
        camera = rep.create.camera(position=(0, 15, 25), look_at=target)

        # Add a Dome Light with a texture for realistic reflections
        light = rep.create.light(
            light_type="Dome",
            intensity=1000,
            texture=assets_root_path + "/Isaac/Environments/Simple_Warehouse/Materials/TexturesCom_Plaster_Concrete_01_2K_albedo.png" if assets_root_path else None
        )

        return target, distractors, camera, light


# --- 2. RANDOMIZATION LOGIC ---
def register_randomizers(target, distractors, camera, light):
    def randomize_props():
        # Randomize Target Position
        with target:
            rep.modify.pose(
                position=rep.distribution.uniform((-8, -9, 0), (8, 10, 2)),
                rotation=rep.distribution.uniform((0, 0, 0), (0, 360, 0))
            )

        # Randomize Distractors (The clutter flies around to create dynamic backgrounds)
        with distractors:
            rep.modify.pose(
                position=rep.distribution.uniform((-8, -9, 0), (8, 10, 2)),
                rotation=rep.distribution.uniform((0, 0, 0), (0, 360, 0))
            )

        # Randomize Lighting (Day/Night cycle)
        with light:
            rep.modify.attribute("inputs:intensity", rep.distribution.normal(800, 200))
            rep.modify.attribute("inputs:color", rep.distribution.uniform((0.7, 0.7, 0.8), (1, 0.9, 0.8)))

        # Randomize Camera
        with camera:
            rep.modify.pose(
                position=rep.distribution.uniform((-9, -10, 1), (9, 10, 8)),
                look_at=target
            )

    rep.randomizer.register(randomize_props)


# --- 3. EXECUTION ---
# Clean up previous runs
OUTPUT_DIR_FINAL = OUTPUT_DIR + "/fancy_run"

writer = rep.WriterRegistry.get("BasicWriter")
writer.initialize(
    output_dir=OUTPUT_DIR_FINAL,
    rgb=True,
    bounding_box_2d_tight=True
)

target_obj, distractor_obj, cam_obj, light_obj = setup_scene()
register_randomizers(target_obj, distractor_obj, cam_obj, light_obj)

writer.attach([rep.create.render_product(cam_obj, (1024, 1024))])

with rep.trigger.on_frame(max_execs=NUM_FRAMES):
    rep.randomizer.randomize_props()

rep.orchestrator.run()