FROM ls6uniwue/py_correction_base_image

COPY entrypoint.sh model.py main.py simplified_main.py test_data.schema.json /data/

ENTRYPOINT ["./entrypoint.sh"]
