import csv
import locale


# TODO: add rtl support
def check_rtl(langcode):
    print("This is experimental")
    rtl_langcodes = ["ar", "he", "fa", "ur", "ps", "ku", "dv", "yi", "sd", "kmr"]
    if langcode in rtl_langcodes:
        return True
    else:
        return False


def tr(csv_file, target_key, langcode):
    f = open(csv_file, newline="")
    locale_csv = csv.DictReader(f=f, delimiter=",")
    for item in locale_csv:
        if item["stringname"] == target_key:
            try:
                if item[langcode] == "":
                    f.close()
                    return item["en"]
                else:
                    f.close()
                    return item[langcode]
            except:
                f.close()
                return item["en"]
