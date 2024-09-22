#!/usr/bin/perl -w

use Net::WebSocket::Server;
use Net::WebSocket::Server::Connection;

my $port = 9900;
print "Starting WebSocket chat server on port $port, press Ctr-C to disconnect\n";

Net::WebSocket::Server->new(
    listen => $port,
    on_connect => sub {
        my ($serv, $conn) = @_;
        $conn->on(
            utf8 => sub {
                my ($conn, $msg) = @_;
                print "got: $msg\n";
                $_->send_utf8($msg) for( $serv->connections() );                
            }, 
        ); 
    },
)->start;




print "Content-type: text/html\n\n";
print "<html><h1>Running</h1></html>\n"
