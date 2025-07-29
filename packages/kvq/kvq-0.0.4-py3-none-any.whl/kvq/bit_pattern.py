import json
import importlib.resources as pkg_resources
from kvq.const import model_dict, supported_models

from .const import _SUPPORTED_BITS

assets_path = "kvq.assets"

def bit_pattern(
    model, budget=4, layers="all", bit_range=_SUPPORTED_BITS, score=0
):
    """
    # Quantizer.SUPPORTED_BITS = range [8, 6, 5, 4, 3, 2, 1.58, 1]

    """

    if model not in supported_models:
        raise ValueError(
            f"Model {model} is not supported. Supported models are: {supported_models}"
        )

    if budget > 8:
        raise ValueError("Budget should be less than or equal to 8 bits.")

    if layers != "all":
        raise NotImplementedError("Only 'all' layers are supported for now.")

    if (model_name := model_dict.get(model)) is None:
        raise ValueError(f"Model {model} is not supported. Please open an issue at ...")


    norm ="frobenius_norm" if score == 0 else  "spectral_norm"
    score_file = f"{norm}/{model_name}.json"
    

    with pkg_resources.files(assets_path).joinpath(score_file).open() as f:
        kv_weights = json.load(f)

    num_layers = len(kv_weights["w_k"])

    total_budget = 2 * budget * num_layers

    n = 2 * num_layers
    sensitivities = []
    for i in range(num_layers):
        sensitivities.append(kv_weights["w_k"][i])
        sensitivities.append(kv_weights["w_v"][i])

    c = [s**2 for s in sensitivities]
    supported_bits = sorted(bit_range)
    next_bit_dict = {}
    for i in range(len(supported_bits) - 1):
        next_bit_dict[supported_bits[i]] = supported_bits[i + 1]

    current_bits = [supported_bits[0]] * n
    total_bits_used = n * supported_bits[0]

    while total_bits_used < total_budget:
        best_gain = -1
        candidate_index = -1
        candidate_next_bit = None
        candidate_additional = 0

        for idx in range(n):
            current_bit_val = current_bits[idx]
            if current_bit_val not in next_bit_dict:
                continue
            next_b = next_bit_dict[current_bit_val]
            additional_bits = next_b - current_bit_val
            if total_bits_used + additional_bits > total_budget:
                continue

            current_distortion = c[idx] * (2 ** (-2 * current_bit_val))
            next_distortion = c[idx] * (2 ** (-2 * next_b))
            reduction = current_distortion - next_distortion
            gain = reduction / additional_bits

            if gain > best_gain:
                best_gain = gain
                candidate_index = idx
                candidate_next_bit = next_b
                candidate_additional = additional_bits

        if candidate_index == -1:
            break

        current_bits[candidate_index] = candidate_next_bit
        total_bits_used += candidate_additional

    w_k_bits = []
    w_v_bits = []
    for i in range(num_layers):
        w_k_bits.append(current_bits[2 * i])
        w_v_bits.append(current_bits[2 * i + 1])

    kv_bits = {"nbits_k": w_k_bits, "nbits_v": w_v_bits}

    # Sanity check
    total_bits_used = sum(w_k_bits) + sum(w_v_bits)
    if total_bits_used != total_budget:
        pass
        # raise ValueError(
        #     f"Total bits used {total_bits_used} does not match budget {total_budget}."
        # )
    print(f"Total bits used: {total_bits_used} (Budget: {total_budget})")

    return kv_bits


if __name__ == "__main__":
    from pathlib import Path

    kv_bits = bit_pattern(
        model="meta-llama/Llama-3.2-1B-Instruct",
        budget=4,
        bit_range=[8, 6, 5, 4, 3, 2, 1.58, 1],
        score=1,  # 0 for frobenius_norm, 1 for spectral_norm
    )

    print(kv_bits)

    print("w_k bits:", kv_bits["w_k"])
    print("w_v bits:", kv_bits["w_v"])
