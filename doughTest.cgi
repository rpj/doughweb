#!/usr/bin/perl

use CGI qw/:all/;
use JSON::XS;
use Data::Dumper;

use lib qw(../libperl/);
use Amazon::SimpleDB;
use Digest::SHA qw(sha1_hex);

my $awsKey = "0639RVH93HXWSTAP9WG2";
my $awsSec = "67eHsTHoFWAgWqE/EluaqQAtalEF8P+Ni7upo3PV";
my $awsDom = 'Dough_Transactions_Test';

my $q = new CGI;
my $response = "";
my $hashSubstrSize = 10;

my $whereConcreteSaveKeys = {url => 1, staticMapUrl => 1, titleNoFormatting => 1, 
    city => 1, region => 1,  country => 1,  streetAddress => 1};

if ($q->request_method() eq "POST")
{
    my $phid = $q->param('phid');
    my $sha = $q->param('sha');
    my $json = decode_json($q->param('json'));

    if ($phid && $sha && $json)
    {
        my $checkSha = sha1_hex($q->param('json'));
        my $parityFault = ($sha eq $checkSha) ? 0 : 1;

        use Amazon::SimpleDB::Client;
        my $sdbServ = Amazon::SimpleDB::Client->new($awsKey, $awsSec);
        
        open (T, "+>>/tmp/doughTest.out") or die "$!\n\n";
        print T "-----\n" . scalar(localtime()). "\n-----\n" . 
            "PhoneID:\t" . $q->param('phid') . "\n" . "SHA-1 Check:\t$sha vs $checkSha ($parityFault)\n";

        foreach my $jHash (@{$json})
        {
            my $jSha = sha1_hex($jHash);
            my $reqHash = {
                DomainName      => $awsDom,
                ItemName        => "${phid}." . substr($checkSha, 0, $hashSubstrSize) . "-" . substr($jSha, 0, $hashSubstrSize),
                Attribute       => []
            };

            if ($parityFault) {
                push (@{$reqHash->{Attribute}}, { Name => "parityFault", Value => "$sha-$checkSha" });
            }

            # loop through the keys given, adding them as attributes, noting special cases such
            # as the 'where' hash, which is complex.
            foreach $jKey (keys(%{$jHash}))
            {
                my $attrRef = $reqHash->{Attribute};

                if ($jKey eq 'where')
                {
                    push (@{$attrRef}, { Name => 'whereAbstract', Value => $jHash->{$jKey}->{abstract} });

                    if ((my $wcHash = $jHash->{$jKey}->{concrete}))
                    {
                        foreach my $wcKey (keys(%{$wcHash}))
                        {
                            if ($whereConcreteSaveKeys->{$wcKey})
                            {
                                push (@{$attrRef}, { Name => "whereConcrete_$wcKey", Value => $wcHash->{$wcKey} });
                            }
                        }
                    }
                }
                else
                {
                    push (@{$attrRef}, { Name => $jKey, Value => $jHash->{$jKey} });
                }
            }

            # run the request against SimpleDB
            eval
            {
                my $resp = $sdbServ->putAttributes($reqHash);

                if ($resp->isSetResponseMetadata() && (my $rMeta = $resp->getResponseMetadata()))
                {
                    print T "ItemName:\t" . ($reqHash->{ItemName}) . "\n";
                    print T "RequestID:\t" . ($rMeta->getRequestId() . "\n"), if ($rMeta->isSetRequestId());
                    print T "BoxUsage:\t" . ($rMeta->getBoxUsage() . "\n"), if ($rMeta->isSetBoxUsage());
                }
            };

            if ((my $ex = $@))
            {
                require Amazon::SimpleDB::Exception;
                $response = "<center><h1>Error 500: Internal Server Error</h1></center>";
                print T "Exception: " . Dumper($ex) . "\n";
                print T "Request: " . Dumper($reqHash) . "\n";
                goto FAIL_OUT;
            }
        }

FAIL_OUT:
        print T "-----\n\n";
        close(T);
    }
    else
    {
        $response = "<center><h1>Error 406: Not Acceptable</h1></center>";
    }
}
else
{
    $response = "<center><h1>Error 405: Method Not Allowed</h1></center>";
}

print $q->header();
print $response;
