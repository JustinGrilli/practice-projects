from pprint import pprint

dictionary = {
  "address": "1013 Brookgreen Dr, Cary NC  27511",
  "advanced": None,
  "archive": None,
  "bad_solve": False,
  "cached_su_json": {
    "cached_su_json": "Manowar/Order/900902/cached_su_json.json"
  },
  "class": "Order",
  "complexity_attributes": {
    "is_mfr": None,
    "roof_square_footage": 1827,
    "total_roof_facets": 25,
    "total_roof_facets_above_4_sqft": 25,
    "walls_square_footage": 0
  },
  "corrections_payload": None,
  "created_at": "2018-09-02 18:15:20 UTC",
  "deliver_time": 45,
  "deliverable_changed": None,
  "deliverable_id": 2,
  "difficulty": "Complex Residential",
  "editable_model": {
    "editable_model": "Manowar/Order/900902/editable_model.skp"
  },
  "failure_reason": None,
  "foundational_plus": False,
  "hyperion_attributes": {},
  "hyperion_job_id": None,
  "id": 900902,
  "image_score": "hard_images",
  "intermediate": False,
  "last_job_uuid": "fed73e8b5db6b3237a99c95f8bc1f60a",
  "local": True,
  "locked_user_id": None,
  "map_attributes": {
    "imagery_dates": [
      "20160906",
      "20170217",
      "20170903",
      "20171110",
      "20180115"
    ],
    "selected_imagery_date": "20180115",
    "source": "nearmap"
  },
  "midas_identifier": None,
  "needs_3d": None,
  "needs_measurements": None,
  "needs_roof_estimate": False,
  "needs_texture": True,
  "notes": "\n[2018-09-02 16:33:10 -0600] New Georef:\n|- Anchor Points: [[35.764657, -78.803101], [35.764652, -78.803002]]\n|--> Geo: [-0.945, 0.326, 0.0, 0.0, -0.326, -0.945, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1667004.481, -6564638.199, 48517.703, 8986.725]\n\n[2018-09-02 16:33:33 -0600] New Georef:\n|- Anchor Points: [[35.764659, -78.803103], [35.764654, -78.803003]]\n|--> Geo: [0.948, -0.32, 0.0, 0.0, 0.32, 0.948, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, -1488920.443, 2881090.327, 48517.703, 8959.675]\n\n[2018-09-02 16:33:55 -0600] New Georef:\n|- Anchor Points: [[35.764654, -78.803], [35.764513, -78.803015]]\n|--> Geo: [0.941, -0.34, 0.0, 0.0, 0.34, 0.941, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, -1448022.584, 2895422.371, 48517.703, 8777.266]\n\n[2018-09-02 16:47:42 -0600] New Georef:\n|- Anchor Points: [[35.764513, -78.803013], [35.764652, -78.803002]]\n|--> Geo: [0.945, -0.328, 0.0, 0.0, 0.328, 0.945, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, -1360875.764, 2983237.016, 1011274.014, 9369.999]\n",
  "number_of_stories": "2 Stories or more",
  "original_order_id": 54013,
  "practice": False,
  "primitives_output": None,
  "primitives_score": None,
  "priority": "10 (Low)",
  "pro_measurements": None,
  "pro_premium_measurements": None,
  "qa_questionnaire": None,
  "reprocess_image": False,
  "results": {
    "results_manowar": "Manowar/Order/900902/results_manowar.json"
  },
  "roof_marker": "POINT (-78.80306334955267 35.76458292350081)",
  "roof_measurements": None,
  "roof_overlay": None,
  "roof_overlay_attributes": None,
  "secret": None,
  "showcase": False,
  "site_id": 29,
  "skip_markups": True,
  "sneaky": True,
  "state": "waiting_qa",
  "tracking_log": {},
  "unlock_vps": False,
  "unlock_vps_reason": None,
  "updated_at": "2018-09-02 23:10:31 UTC"
}

pprint(dictionary)