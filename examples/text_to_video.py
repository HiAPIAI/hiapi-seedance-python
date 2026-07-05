from hiapi_seedance import Seedance

client = Seedance()

task = client.text_to_video(
    prompt="A 30-second cinematic one-take product film, golden hour, slow dolly in.",
    duration=30,
    aspect_ratio="16:9",
    resolution="1080p",
)

print(task.output[0].url)
