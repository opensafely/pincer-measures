import os

indicators_list = ["a", "b", "c", "d", "g", "i",
                   "k", "ac", "me_no_fbc", "me_no_lft", "am", "li"]

backend = os.getenv("OPENSAFELY_BACKEND", "expectations")
