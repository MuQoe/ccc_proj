import json
import pandas as pd


def get_ancestry_correlation(twitter_geo_data):
    ancestry = pd.read_csv('./data/sudo/abs_2021census_g08_aust_gccsa-7258156891153262423.csv')
    # convert twitter_geo_data to pandas
    twitter_geo_data = pd.DataFrame(twitter_geo_data)
    twitter_geo_data = twitter_geo_data.transpose()
    twitter_geo_data = twitter_geo_data.reset_index()
    emoji = twitter_geo_data.drop([11, 12, 13, 15])
    emoji = emoji[['index', 'percentage']]
    ancestry = ancestry.rename(columns=lambda x: x.strip())
    ancestry = ancestry.drop([11, 12, 13, 15]).drop('other_tot_resp', axis=1)
    ancestry = ancestry.set_index('gccsa_code_2021')
    columns = ancestry.columns.tolist()
    columns.remove('tot_p_tot_resp')
    percent_ancestry = ancestry[columns].div(ancestry.tot_p_tot_resp, axis=0)
    df_merged = pd.merge(emoji, percent_ancestry, left_on='index', right_on=percent_ancestry.index)
    correlations = {}

    for column in percent_ancestry.columns:
        corr = df_merged[column].corr(df_merged['percentage'])
        correlations[column] = corr
    correlation_df = pd.DataFrame.from_dict(correlations, orient='index', columns=['correlation_coefficient'])
    correlation_df.sort_values(by='correlation_coefficient')

    # convert back to json
    correlation_df = correlation_df.reset_index()
    correlation_df = correlation_df.rename(columns={'index': 'ancestry'})
    correlation_df = correlation_df.to_json(orient='records')
    return json.loads(correlation_df)


def get_language_correlation(twitter_geo_data):
    twitter_geo_data = pd.DataFrame(twitter_geo_data)
    twitter_geo_data = twitter_geo_data.transpose()
    twitter_geo_data = twitter_geo_data.reset_index()
    emoji = twitter_geo_data.drop([11, 12, 13, 15])
    emoji = emoji[['index', 'percentage']]

    language1 = pd.read_csv(
        './data/sudo/gccsa_g13c_lang_spoken_at_home_by_profic_by_sex_census_2016-3187099501507819260.csv')
    language2 = pd.read_csv(
        './data/sudo/gccsa_g13d_lang_spoken_at_home_by_profic_by_sex_census_2016-1802228558107494941.csv')

    language = pd.merge(language1, language2, on=' gcc_code16')
    language = language.rename(columns=lambda x: x.strip())
    language = language.drop([11, 12, 13, 15])
    language = language.set_index('gcc_code16')
    columns = language.columns.tolist()
    columns.remove('person_tot_tot')
    percent_language = language[columns].div(language.person_tot_tot, axis=0)
    df_merged = pd.merge(emoji, percent_language, left_on='index', right_on=percent_language.index)
    correlations = {}

    for column in percent_language.columns:
        corr = df_merged[column].corr(df_merged['percentage'])
        correlations[column] = corr
    correlation_df = pd.DataFrame.from_dict(correlations, orient='index', columns=['correlation_coefficient'])
    correlation_df.sort_values(by='correlation_coefficient')

    # convert back to json
    correlation_df = correlation_df.reset_index()
    correlation_df = correlation_df.rename(columns={'index': 'language'})
    correlation_df = correlation_df.to_json(orient='records')
    return json.loads(correlation_df)


with open('./data/twitter/twit_emoji_all.json') as f:
    TWITTER_ALL_EMOJI = json.load(f)
    f.close()

with open('./data/twitter/twit_emoji_negative.json') as f:
    TWITTER_NEGATIVE_EMOJI = json.load(f)
    f.close()

with open('./data/twitter/twit_emoji_posistive.json') as f:
    TWITTER_POSITIVE_EMOJI = json.load(f)
    f.close()

with open('./data/twitter/twit_emoji_neutral.json') as f:
    TWITTER_NEUTRAL_EMOJI = json.load(f)
    f.close()

TWITTER_SENTIMENT_DATA = {
    "Negative": TWITTER_NEGATIVE_EMOJI,
    "Positive": TWITTER_POSITIVE_EMOJI,
    "Neutral": TWITTER_NEUTRAL_EMOJI,
}

LANGUAGE_MAP = {"person_spks_afrikaans_tot": "Afrikaans", "person_spks_arabic_tot": "Arabic",
         "person_spks_aus_indig_lang_tot": "Australian Indigenous Languages",
         "person_spks_cl_tot_tot": "Chinese Languages", "person_spks_croatian_tot": "Croatian",
         "person_spks_dutch_tot": "Dutch", "person_spks_french_tot": "French",
         "person_spks_eng_only_tot": "English only", "person_spks_german_tot": "German",
         "person_spks_greek_tot": "Greek", "person_spks_indo_aryan_lang_tot_tot": "Indo Aryan Languages",
         "person_spks_indo_aryan_lang_urdu_tot": " Urdu", "person_spks_italian_tot": "Italian",
         "person_spks_japanese_tot": "Japanese", "person_spks_korean_tot": "Korean",
         "person_spks_macedonian_tot": "Macedonian", "person_spks_maltese_tot": "Maltese",
         "person_spks_polish_tot": "Polish", "person_spks_persian_ed_tot": "Persian",
         "person_spks_russian_tot": "Russian", "person_spks_samoan_tot": "Samoan",
         "person_spks_se_asia_austronesia_lang_tot_tot": "Southeast Asian Austronesian Languages",
         "person_spks_serbian_tot": "Serbian", "person_spks_spanish_tot": "Spanish", "person_spks_tamil_tot": "Tamil",
         "person_spks_thai_tot": "Thai", "person_spks_turkish_tot": "Turkish",
         "person_spks_vietnamese_tot": "Vietnamese"
                }

ANCETRY_MAP = {"aust_tot_resp": "Australian", "croatian_tot_resp": "Croatian", "dutch_tot_resp": 'Dutch',
        "french_tot_resp": "French", "filipino_tot_resp": "Filipino", "english_tot_resp": "English",
        "german_tot_resp": "German", "greek_tot_resp": "Greek", "hungarian_tot_resp": "Hungarian",
        "indian_tot_resp": "Indian", "irish_tot_resp": "Irish", "italian_tot_resp": "Italian",
        "korean_tot_resp": "Korean", "lebanese_tot_resp": "Lebanese", "macedonian_tot_resp": "Macedonian",
        "maltese_tot_resp": "Maltese", "maori_tot_resp": "Maori", "nz_tot_resp": "New Zealander",
        "polish_tot_resp": "Polish", "russian_tot_resp": "Russian", "samoan_tot_resp": "Samoan",
        "scottish_tot_resp": "Scottish", "serbian_tot_resp": "Serbian", "sth_african_tot_resp": "South African",
        "spanish_tot_resp": "Spanish", "sri_lankan_tot_resp": "Sri_Lankan", "vietnamese_tot_resp": "Vietnamese",
        "welsh_tot_resp": "Welsh", "chinese_tot_resp": "Chinese"}