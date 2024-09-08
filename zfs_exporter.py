from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ZFSExporter(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

    def _run_command(self, command):
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True)
            return result.stdout.decode('utf-8')
        except subprocess.CalledProcessError as e:
            logger.error(f"Command '{command}' failed: {e.stderr.decode('utf-8')}")
            return ""

    def _safe_int(self, value):
        try:
            return int(value)
        except ValueError:
            return None

    def _parse_zpool_status(self):
        output = self._run_command('zpool list -Hp')
        pools = []
        for line in output.strip().split('\n'):
            fields = line.split('\t')
            if len(fields) >= 9:  # Ensure we have enough fields
                pools.append({
                    'name': fields[0],
                    'size': self._safe_int(fields[1]),
                    'allocated': self._safe_int(fields[2]),
                    'free': self._safe_int(fields[3]),
                    'fragmentation': self._safe_int(fields[4]),
                    'capacity': self._safe_int(fields[5]),
                    'health': fields[8]
                })
            else:
                logger.warning(f"Unexpected zpool output format: {line}")
        return pools

    def _parse_zfs_filesystems(self):
        output = self._run_command('zfs list -Hp')
        filesystems = []
        for line in output.strip().split('\n'):
            fields = line.split('\t')
            if len(fields) >= 5:  # Ensure we have enough fields
                filesystems.append({
                    'name': fields[0],
                    'used': self._safe_int(fields[1]),
                    'available': self._safe_int(fields[2]),
                    'refer': self._safe_int(fields[3]),
                    'mountpoint': fields[4]
                })
            else:
                logger.warning(f"Unexpected zfs filesystem output format: {line}")
        return filesystems

    def do_GET(self):
        self._set_headers()

        try:
            pools = self._parse_zpool_status()
            filesystems = self._parse_zfs_filesystems()

            # Export ZFS pool metrics
            for pool in pools:
                for metric in ['size', 'allocated', 'free']:
                    if pool[metric] is not None:
                        self.wfile.write(f'zfs_pool_{metric}_bytes{{pool="{pool["name"]}"}} {pool[metric]}\n'.encode('utf-8'))
                if pool['fragmentation'] is not None:
                    self.wfile.write(f'zfs_pool_fragmentation_percent{{pool="{pool["name"]}"}} {pool["fragmentation"]}\n'.encode('utf-8'))
                if pool['capacity'] is not None:
                    self.wfile.write(f'zfs_pool_capacity_percent{{pool="{pool["name"]}"}} {pool["capacity"]}\n'.encode('utf-8'))
                self.wfile.write(f'zfs_pool_health_status{{pool="{pool["name"]}"}} {1 if pool["health"] == "ONLINE" else 0}\n'.encode('utf-8'))

            # Export ZFS filesystem metrics
            for fs in filesystems:
                for metric in ['used', 'available', 'refer']:
                    if fs[metric] is not None:
                        self.wfile.write(f'zfs_filesystem_{metric}_bytes{{filesystem="{fs["name"]}"}} {fs[metric]}\n'.encode('utf-8'))
                self.wfile.write(f'zfs_filesystem_mountpoint{{filesystem="{fs["name"]}", mountpoint="{fs["mountpoint"]}"}} 1\n'.encode('utf-8'))

            logger.info("Metrics exported successfully")
        except Exception as e:
            logger.error(f"Error while exporting metrics: {e}")
            self.wfile.write(f"# Error: {str(e)}\n".encode('utf-8'))

def run(server_class=HTTPServer, handler_class=ZFSExporter, port=9134):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logger.info(f'Starting ZFS exporter on port {port}')
    httpd.serve_forever()

if __name__ == "__main__":
    run()