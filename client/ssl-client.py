#!/usr/local/bin/python

import argparse
import logging
import json
import ssl
import socket
import pprint
import sys

ca_file = 'ssl/ca-bingo-ca.pem'
server_host = 'u1.bingo.ericsson.se'
server_port = 13443

def send_data(options=0):
  context = ssl.SSLContext(ssl.PROTOCOL_TLS)
  context.verify_mode = ssl.CERT_REQUIRED
  context.check_hostname = True
  context.load_verify_locations(ca_file)

  context.options |= options
  
  conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=server_host)
  try:
    conn.connect((server_host, server_port))
  except ssl.CertificateError as ce:
    logger.error('ssl certificate error:', ce)
    sys.exit()
  except Exception as e:
    logger.error('Unexpected error:')
    print sys.exc_info()[0]
    print e
    sys.exit()
  
  logger.info('connected to %s:%d successfully.' % (server_host, server_port))
  logger.info('ssl version used: %s' % (conn.version(),))
  
  cert = conn.getpeercert()
  logger.debug('server certificate recieved: ' + json.dumps(cert))
  
  logger.debug('sending request')
  conn.sendall('ping\n')
  logger.debug('request sent')
  
  data = conn.recv()
  logger.info('response from server: %s' % (data,))
  logger.debug('all finished.')

if __name__ == '__main__':
  # Default setting for logging.
  log_level = logging.INFO
  FORMAT = '%(asctime)-15s [%(name)-12s] %(levelname)-8s %(message)s'
  logging.basicConfig(level=log_level, format=FORMAT)
  logger = logging.getLogger(sys.argv[0])

  parser = argparse.ArgumentParser(prefix_chars='-+', \
    formatter_class=argparse.RawTextHelpFormatter, \
    description='Description:\n\tssl/tls client for tests. (EXANTNG)')
    
  parser.add_argument('-d', '--debug', action='store_true', help='enable debug mode.')
  
  group = parser.add_mutually_exclusive_group()
  group.add_argument('-0', '--tls1.0', action='store_true', dest='tls1_0', help='use TLSv1.1 only.')
  group.add_argument('-1', '--tls1.1', action='store_true', dest='tls1_1', help='use TLSv1.1 only.')
  group.add_argument('-2', '--tls1.2', action='store_true', dest='tls1_2', help='use TLSv1.2 only.')
  group.add_argument('-3', '--tls1.3', action='store_true', dest='tls1_3', help='use TLSv1.3 only.')
  group.add_argument('-s2', '--ssl2.0', action='store_true', dest='ssl2_0', help='use SSLv2.0 only.')
  group.add_argument('-s3', '--ssl3.0', action='store_true', dest='ssl3_0', help='use SSLv3.0 only.')

  args = parser.parse_args()

  if args.debug == True:
    logger.setLevel(logging.DEBUG)
    logger.debug('Debug mode enabled.')

  options = 0
  if args.tls1_0:
    logger.info('set to TLSv1.0 only')
    options |= (ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2 | ssl.OP_NO_TLSv1_3)
  if args.tls1_1:
    logger.info('set to TLSv1.1 only')
    options |= (ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_2 | ssl.OP_NO_TLSv1_3)
  if args.tls1_2:
    logger.info('set to TLSv1.2 only')
    options |= (ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_3)
  if args.tls1_3:
    logger.info('set to TLSv1.3 only')
    options |= (ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2)
  if args.ssl2_0:
    logger.info('set to SSLv2.0 only')
    options |= (ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2 | ssl.OP_NO_TLSv1_3)
  if args.ssl3_0:
    logger.info('set to SSLv3.0 only')
    options |= (ssl.OP_NO_SSLv2 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2 | ssl.OP_NO_TLSv1_3)

  send_data(options)