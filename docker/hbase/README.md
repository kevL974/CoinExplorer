# How to run Hbase container
## 1. **Build hbase image :**
<p><code>docker build . -t opa_hbase</code></p>

## 2. **Run image :**

<p><code>docker run -d  -p 16000:16000 -p 16010:16010 -p 16020:16020 -p 16030:16030 -p 9090:9090 -v /path/to/local/data:/data --name opa_datawarehouse opa_hbase</code></p>
Replace /path/to/local/data with the path to the local directory where you want to store the HBase data.

Example: 
<p><code>docker run -d  -p 16000:16000 -p 16010:16010 -p 16020:16020 -p 16030:16030 -p 9090:9090 -v /data:/data --name opa_datawarehouse opa_hbase</code></p>

## 3. Delete Hbase container
<p><code>docker container rm $(docker container stop opa_datawarehouse)</code></p>