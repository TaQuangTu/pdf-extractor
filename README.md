### PDF Extractor

Extract signer, signing date and N.O of popularly Vietnamese-styled announcements in PDF documents.

### Prerequisite
Setup environment
```bash
pip install -r requirements.txt
```

### Inference

Start HTTP service

```bash
python deploy.py -i 0.0.0.0 -p 4444 
```

Extract info

```text
Method: POST
Endpoint: /extract
```

#### Body

Form-data | value | Description |
--- | --- | --- |
file | `pdf_file` | byte array of a pdf file | 
ratio | "20,1" | a string contains two comma separated integer numbers.
threshold | "0.7" | threshold to filter unconfident text.

#### Sample result

Each field contains a list of possible values.

```json
{
    "date": ["Quang Nam, ngày 09 tháng 02 năm 2023"],
    "no": ["Số: 334/TB-SGTVT"],
    "signer": ["Nguyễn Thị Giám Đốc"]
}
```