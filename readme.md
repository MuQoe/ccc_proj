## Project structure and files

```
ccc_proj
│
├── data                                    # Static data files
│   ├── sudo                                # static data for SUDO
│   │   ├── abs_2021census_g08_aust_gccsa-7258156891153262423.csv
│   │   ├── gccsa_g13c_lang_spoken_at_home_by_profic_by_sex_census_2016-3187099501507819260.csv
│   │   └── gccsa_g13d_lang_spoken_at_home_by_profic_by_sex_census_2016-1802228558107494941.csv
│   ├── twitter                             # static data for Twitter
│   │   ├── twit_emoji_all.json
│   │   ├── twit_emoji_negative.json
│   │   ├── twit_emoji_neutral.json
│   │   └── twit_emoji_posistive.json
│   └──  data.py                            # data access entry file
├── logs                                    # logs folder
│   └──  logs.log
├── static                                  # static files
├── utils                                   # utils folder
│   ├── database.py                         # database connection and query
│   ├── response.py                         # response formater
│   └── sentiment.py                        # sentiment analysis
├── views                                   # database views folder
│   └── views.py                            # register views
├── app.py                                  # app entry file
├── build.sh                                # docker build script
├── run.sh                                  # docker run script
├── stop.sh                                 # docker stop script
├── remove.sh                               # docker remove script
├── requirements.txt                        # python dependencies
└──  Dockerfile                             # docker file
```