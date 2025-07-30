
import soundfile as sf
import numpy as np
from fujielab.asr_parallel_cbs.espnet_ext.espnet2.bin.asr_parallel_transducer_inference import Speech2Text
from scipy.signal import resample
from os import path

model_name = "fujie/espnet_asr_parallel_cbs_transducer_848_finetune_raw_jp_char_sp"

s2t = Speech2Text.from_pretrained(
    model_name,
    streaming=True,
    beam_search_config=dict(search_type="maes"),
    lm_weight=0.0,
    beam_size=10,
    nbest=1,
)

if not path.exists("aps-smp.mp3"):
    # Download a sample audio file
    # from https://clrd.ninjal.ac.jp/csj/sound-f/aps-smp.mp3
    import requests
    url = "https://clrd.ninjal.ac.jp/csj/sound-f/aps-smp.mp3"
    response = requests.get(url)
    with open("aps-smp.mp3", "wb") as f:
        f.write(response.content)


audio, fs = sf.read("aps-smp.mp3")
if fs != 16000:
    # Resample the audio to 16000 Hz
    num_samples = len(audio)
    audio = resample(audio, int(num_samples * 16000 / fs))
    fs = 16000

num_samples = len(audio)
chunk_size = 16000 * 1/10  # 100ms

final_text = ""
for i in range(0, num_samples, int(chunk_size)):
    chunk = audio[i:i+int(chunk_size)]
    is_final = False
    if len(chunk) < int(chunk_size):
        chunk = np.pad(chunk, (0, int(chunk_size) - len(chunk)), "constant")
        is_final = True
    parallel_hyps = s2t.streaming_decode(chunk, is_final=is_final)
    hyps = parallel_hyps[2] if parallel_hyps[2] else parallel_hyps[1]

    results = s2t.hypotheses_to_results(hyps)
    if len(results) > 0:
        print(results[0][0])
        final_text = results[0][0]

print("Final text:", final_text)

