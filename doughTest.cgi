#!/usr/bin/perl -Wall

use CGI qw/:all/;
use JSON::XS;
use Data::Dumper;
use Digest::SHA qw(sha1_hex);

use lib qw(../libperl/);
use Amazon::SimpleDB;
use Amazon::SimpleDB::Client;

my $k_awsKey = "0639RVH93HXWSTAP9WG2";
my $k_awsSec = "67eHsTHoFWAgWqE/EluaqQAtalEF8P+Ni7upo3PV";
my $k_awsTADom = 'Dough_Transactions_Test';
my $k_awsUserDom = 'Dough_Users';

my $g_response = "";
my $g_hashSubstrSize = 15;

my $g_whereConcreteSaveKeys = {url => 1, staticMapUrl => 1, titleNoFormatting => 1, 
    city => 1, region => 1,  country => 1,  streetAddress => 1};

my $g_q = new CGI;
my $g_sdbServ = Amazon::SimpleDB::Client->new($g_awsKey, $g_awsSec);

sub sendPutAttrReqToSDB($)
{
	my $reqHash = shift;
	
	eval
	{
		my $resp = $g_sdbServ->putAttributes($reqHash);
		
		if ($resp->isSetResponseMetadata() && (my $rMeta = $resp->getResponseMetadata()))
		{
			print T "\nItemName:\t" . ($reqHash->{ItemName}) . "\n";
			print T "RequestID:\t" . ($rMeta->getRequestId() . "\n"), if ($rMeta->isSetRequestId());
			print T "BoxUsage:\t" . ($rMeta->getBoxUsage() . "\n"), if ($rMeta->isSetBoxUsage());
		}
	};
	
	if ((my $ex = $@))
	{
		require Amazon::SimpleDB::Exception;
		$g_response = "<center><h1>Error 500: Internal Server Error</h1></center>";
		print T "Exception: " . Dumper($ex) . "\n";
		print T "Request: " . Dumper($reqHash) . "\n";
		return 0;
	}
	
	return 1;
}

sub procTA($$$)
{
	my ($phid, $sha, $json) = @_;
	my $checkSha = sha1_hex($g_q->param('json'));
	my $parityFault = ($sha eq $checkSha) ? 0 : 1;
	
	print T "SHA-1 Check:\t$sha vs $checkSha ($parityFault)\n";
	
	foreach my $jHash (@{$json})
	{
		my $jSha = sha1_hex(%{$jHash});
		my $reqHash = {
			DomainName      => $g_awsTADom,
			ItemName        => substr($checkSha, 0, $g_hashSubstrSize - 5) . "-" . substr($jSha, 0, $g_hashSubstrSize + 5),
			Attribute       => [
			{
				Name    => "deviceID",
				Value   => $phid
			}
			]
		};
		
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
						if ($g_whereConcreteSaveKeys->{$wcKey})
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
		if (!sendPutAttrReqToSDB($reqHash))
		{
			return 0;
		}
	}
	
	return 1;
}

if ($q->request_method() eq "POST")
{
    my $phid = $g_q->param('phid');
    my $sha = $g_q->param('sha');
	my $act = $g_q->param('act');
    my $json = decode_json($g_q->param('json'));
	
	open (T, "+>>/tmp/doughTest.out") or die "$!\n\n";
	print T "-----\n" . scalar(localtime()). "\n-----\n" . 
		"PhoneID:\t$phid\n" . "TA Domain:\t$g_awsTADom\nUser Domain:\t$g_awsUserDom\n";

    if ($phid && $sha && $json) 
	{
		if ($act eq 'ta' && $json)				# new transaction
		{
			goto FAIL_OUT, if (!procTA($phid, $sha, $json));
		}
		elsif ($act eq 'nu')					# new user
		{
		}
		else
		{
		}
    }
    else
    {
        $g_response = "<center><h1>Error 406: Not Acceptable</h1></center>";
    }
}
else
{
    $g_response = "<center><h1>Error 405: Method Not Allowed</h1></center>";
}

FAIL_OUT:
	print T "-----\n\n";
	close(T);

print $g_q->header();
print $g_response;
