# 🎵 Top 100 US-UK Artists - YouTube Data ETL Pipeline

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Google Cloud](https://img.shields.io/badge/Google_Cloud-VM_%7C_Storage-4285F4.svg)
![YouTube API](https://img.shields.io/badge/YouTube_Data_API-v3-red.svg)
![Data Engineering](https://img.shields.io/badge/Data-ETL_Pipeline-green.svg)

## 📌 Tổng quan Dự án (Project Overview)
Dự án là một hệ thống Data Pipeline toàn diện (End-to-End ETL) nhằm tự động hóa việc thu thập, xử lý và lưu trữ dữ liệu từ YouTube của Top 100 nghệ sĩ US-UK. Hệ thống giúp theo dõi các chỉ số quan trọng (lượt đăng ký, lượt xem, thông tin video, và bình luận), phục vụ trực tiếp cho việc phân tích và trực quan hóa trên Dashboard.

**Tác giả:** Nguyễn Đoàn Hải Dương (Danny)

---

## 🔄 Kiến trúc Hệ thống (Architecture Flowchart)

Hệ thống được thiết kế theo mô hình E-T-L (Extract - Transform - Load), vận hành tự động trên máy chủ Google Cloud (GCP VM) thông qua Crontab.

```mermaid
graph TD
    A[YouTube Data API v3] -->|Extract| B(Data Lake / Thư mục Local)
    
    subgraph ETL Pipeline [Python Automation]
        B -->|Read| C[Transform Layer]
        C -->|Clean, Format & Aggregate| D[Transformed Data]
        D -->|Load| E[(Data Warehouse / Database)]
    end
    
    E -->|Live Connection| F[BI Tool]
    F -->|Visualize| G((Interactive Dashboard))
    
    classDef source fill:#f9d0c4,stroke:#333,stroke-width:2px;
    classDef process fill:#d4e157,stroke:#333,stroke-width:2px;
    classDef db fill:#81d4fa,stroke:#333,stroke-width:2px;
    classDef dashboard fill:#ce93d8,stroke:#333,stroke-width:2px;
    
    class A source;
    class C,D process;
    class E db;
    class G dashboard;

📦 BIG_PROJECT_1_DUONG_DANNY
 ┣ 📂 ETL_Top_100
 ┃ ┣ 📜 config.py               # Chứa các tham số hệ thống và đường dẫn
 ┃ ┣ 📜 a.extract.py            # Master script điều phối quá trình Extract
 ┃ ┣ 📜 b_channel_extract.py    # Crawl dữ liệu kênh (Subscribers, Views,...)
 ┃ ┣ 📜 c_video_extract.py      # Crawl dữ liệu video chi tiết
 ┃ ┗ 📜 d_comment_extract.py    # Crawl bình luận người dùng
 ┣ 📜 Transform_artists.py      # Module làm sạch dữ liệu Kênh
 ┣ 📜 Transform_video.py        # Module xử lý Missing values & Formatting
 ┣ 📜 Transform_comment.py      # Module xử lý Text Analytics
 ┣ 📜 Load_artists.py           # Module đẩy dữ liệu lên Database/Kho lưu trữ
 ┣ 📜 Load_video.py             
 ┣ 📜 Load_comment.py           
 ┣ 📜 main.py                   # Script điều phối toàn bộ quy trình ETL
 ┣ 📜 run_pipeline.sh           # Bash script để tự động hóa trên Linux/VM
 ┣ 📜 requirements.txt          # Danh sách thư viện Python
 ┣ 📜 .gitignore                # Quản lý các file ẩn và file data lớn (*.csv)
 ┗ 📜 pipeline.log              # Nhật ký vận hành hệ thống (Log file)

git clone [https://github.com/Danny-AI28/Top-100-US-UK-artists-youtube-information.git](https://github.com/Danny-AI28/Top-100-US-UK-artists-youtube-information.git)
cd Top-100-US-UK-artists-youtube-information

# Tạo môi trường ảo
python3 -m venv myenv

# Kích hoạt (Trên Linux/macOS)
source myenv/bin/activate
# Kích hoạt (Trên Windows)
# myenv\Scripts\activate

# Cài đặt thư viện
pip install -r requirements.txt

YOUTUBE_API_KEY=your_api_key_here
DB_CONNECTION_STRING=your_database_url_here

### Chạy Pipeline (Execution)

**Chạy thủ công:**
```bash
python3 main.py

### Chay tu dong

chmod +x run_pipeline.sh
crontab -e
crontab -e
0 16 * * * /đường_dẫn_tuyệt_đối_đến_thư_mục_project/run_pipeline.sh