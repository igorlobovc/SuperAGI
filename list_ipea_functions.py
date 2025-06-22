import ipeadatapy as ipea

print("Available functions/attributes in ipeadatapy:")
for attr in dir(ipea):
    if not attr.startswith('_'): # Exclude private/special attributes
        print(attr)
