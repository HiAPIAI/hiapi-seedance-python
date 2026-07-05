from hiapi_seedance import Seedance

client = Seedance()

task = client.image_to_video(
    prompt="Animate the reference image with a slow push-in and warm rim light.",
    image_urls=["https://example.com/first-frame.png"],
    duration=8,
    aspect_ratio="9:16",
)

print(task.output[0].url)
