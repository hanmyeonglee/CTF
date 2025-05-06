import requests

cookies = {
    "_ga": "GA1.1.544669744.1731145827",
    "__cf_bm": "LZCN1vLpQfq168_DQ6zWF5XVnB._pgA.0M6Gp33mcOA-1731201844-1.0.1.1-c_hqWoqr41yx2tJ1_wkvNy52ViRcm80Z7ZEdEAtCPoTlK9wh.8_PvMbmBfqAoAz9PWVG6zqGGmt26a_XzxxzvA",
    "cf_clearance": "WkSRoKDe8NhL2vzMcWc7oYquPDdjcus.W91ZEEpfZjk-1731201847-1.2.1.1-2v.CZtpRjxUkq8rl078AUYlZIRXQulErK4_GbY_xBD1pasVWpbTgD0zAeHK7_5AMjupbgGSi5fg0PAt6hAZNlGlAfFcP52H0nunLgGar2ISIAitlzZsMOKF1dWIBKkOD0W1uT2fT9Z4yUDCXKGDqW32Q.jkephDX8kCP3CT2GcYKpWV_fE9XpgkZbR.RHiBQxXhoWYXEUtxFcv2j0kgI3CZC4iQHQFi5UQlTBw6pV9oMEul_dzpJAYjo4.T_FaHyaIEv52nNGFqyUfLjUzYsmiIfLosZYLW1kk6aK.0x0y1flOTkOSSdJxpsQPoQBmLdgkVqEWh0OmqThi65klKRO6J94TER4Yyb4MBf.RTKCySCzEaj5sbThYtRutWUnJkl2zcrpHb9RxxTDlsbK.PZUQ",
    "__gads": "ID=60446133642a481e:T=1731145837:RT=1731201852:S=ALNI_MZFCAlMpXeh6K7q_QjWog1z0G5uJg",
    "__gpi": "UID=00000f645cd76a68:T=1731145837:RT=1731201852:S=ALNI_MYR-RMgZlRpzguCSFwUgRKC3u9BSw; __eoi=ID=3236df2d6df24a78:T=1731145837:RT=1731201852:S=AA-AfjagIpNY_jv1sz17NN-tivZd; _ga_L7MJCSDHKV=GS1.1.1731201848.4.0.1731201855.0.0.0",
    "FCNEC": "%5B%5B%22AKsRol-pHk3qMA9Kme6s3Kt6ukAUtynJoTjSgkW42StHS2u_h8XkHvH9ekmUEsEl9e2DDraZGNks0PuIjaBI-dCYruooViYpLBnEG7AYoD0CXnZjgalLZIBT3IAbPwOdOoMPojoJ923bcTCHD2MMxb31RfOcsBiUMw%3D%3D%22%5D%5D"
}

path = 'https://neal.fun/api/infinite-craft/pair'

res = requests.get(
    path,
    cookies=cookies,
    params={
        'first': 'Mountain',
        'second': 'Mountain'
    }
)

print(res.text)