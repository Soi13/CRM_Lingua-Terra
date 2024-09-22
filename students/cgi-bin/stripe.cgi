#!/Perl64/bin/perl -w
use strict;
use DBI;
use CGI;
use CGI qw (:standart);
use CGI qw(:cgi);
#use CGI::Carp qw(fatalsToBrowser);
use JSON;
use ConnectDB;
use CGI::Session;
use Encode;
use REST::Consumer;

my $cgi=CGI->new;

# Required parameters:
my $client = REST::Consumer->new(
        host => 'https://api.stripe.com'
     
); 
 
my $deserialized_result = $client->post(
      path => '/v1/payment_intents',
      headers => [
                'Authorization' => '',
                'Content-Type' => 'application/json',
                'Host' => 'api.stripe.com'
        ],
       params => {
             amount => 100,
             currency => 'usd'			 
       },
);


my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ clientSecret => $deserialized_result->{'client_secret'} });

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");
print $json;


__END__
