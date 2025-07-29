import zarr
filename = r'https://s3.embl.de/bls-app-test/test.bls.zarr'

import fsspec
import s3fs
fs = fsspec.filesystem('s3', anon=True,
                       client_kwargs={'endpoint_url': 'https://s3.embl.de'})

#store = zarr.storage.FsspecStore.from_url(url=filename, read_only=True)
store = s3fs.S3Map(root=r"bls-app-test/test.bls.zarr", s3=fs, check=False)
#print(f"listing supported: {store.supports_listing}")

root = zarr.open_group(store=store, mode='r')

root["Brillouin_data"] # the key 'Brillouin_data' can e found
print(f"keys: {list(root.keys())}") # but when listing the keys in the root an empty list is returned