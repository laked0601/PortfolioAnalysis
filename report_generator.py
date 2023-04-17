
micro_rgb_params = ((1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1))
short_rgb_params = (1, 0.5, 0.75, 0.875, 0.625, 0.9375, 0.5625)
short_params_len = len(short_rgb_params) * len(micro_rgb_params)


def short_rgb_loop(stop=short_params_len):
    count = 0
    for sht in short_rgb_params:
        for mic in micro_rgb_params:
            yield [i * sht for i in mic]
            count += 1
            if count >= stop:
                break
        if count >= stop:
            break

