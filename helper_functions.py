"""This a collection of small function used in various parts of the project."""
import constants as c

def flag_to_str(flag):
    return "enabled" if flag == c.FLAG_ENABLED else "disabled"

def score_to_str(correct,total):
    try:
        score =  float(0 if int(total) == 0 else int(correct)*100/int(total))
        return f"{score:.1f} %"
    except ValueError:
        return "0.0 %"
    