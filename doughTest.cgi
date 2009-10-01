#!/usr/bin/perl

use Time::HiRes qw(gettimeofday tv_interval);
my $t0 = [gettimeofday];

use lib qw(/home/sulciphur/lib/perl5/lib/x86_64-linux-gnu-thread-multi);

use CGI qw/:all/;
use JSON::XS;
use Data::Dumper;
use Digest::SHA qw(sha1_hex);

use Amazon::SimpleDB::Client;

my $k_awsKey = "";
my $k_awsSec = "";
my $k_awsTADom = 'Dough_Transactions_Test';
my $k_awsUserDom = 'Dough_Users_Test';
my $k_logFile = '/home/sulciphur/wlogs/doughTest.log';

my $g_response = undef;
my $g_hashSubstrSize = 15;

my $g_whereConcreteSaveKeys = {url => 1, staticMapUrl => 1, titleNoFormatting => 1, 
    city => 1, region => 1,  country => 1,  streetAddress => 1};

my $g_q = new CGI;
my $g_sdbServ = Amazon::SimpleDB::Client->new($k_awsKey, $k_awsSec);

sub sendReqToSDB($$)
{
	my $reqHash = shift;
    my $reqFunc = shift;
    my $retVal = 0;
	
	eval
	{
        # funky way of calling a class method, but these here are funky "classes"
        print T "\n";
        print T "Domain:\t\t" . $reqHash->{DomainName} . "\n";

		my $resp = &$reqFunc($g_sdbServ, $reqHash);
		
		if ($resp->isSetResponseMetadata() && (my $rMeta = $resp->getResponseMetadata()))
		{
			print T "ItemName:\t" . ($reqHash->{ItemName}) . "\n", if ($reqHash->{ItemName});
			print T "RequestID:\t" . ($rMeta->getRequestId() . "\n"), if ($rMeta->isSetRequestId());
			print T "BoxUsage:\t" . ($rMeta->getBoxUsage() . "\n"), if ($rMeta->isSetBoxUsage());
		}

        $retVal = $resp;
	};
	
	if ((my $ex = $@))
	{
		require Amazon::SimpleDB::Exception;
		$g_response = "<center><h1>Error 500: Internal Server Error</h1></center>";
		print T "Exception: " . Dumper($ex) . "\n";
		print T "Request: " . Dumper($reqHash) . "\n";
	    $retVal = 0;
	}
	
	return $retVal;
}

sub sendPutAttrReqToSDB($)
{
    return sendReqToSDB(shift, \&Amazon::SimpleDB::Client::putAttributes);
}

sub procTA($$$)
{
	my ($phid, $sha, $json) = @_;
	my $checkSha = sha1_hex($g_q->param('json'));
	my $parityFault = ($sha eq $checkSha) ? 0 : 1;
    my $retVal = 0;
	
	print T "SHA-1 Check:\t$sha vs $checkSha ($parityFault)\n";
	
	foreach my $jHash (@{$json})
	{
		my $jSha = sha1_hex(%{$jHash});
		my $reqHash = {
			DomainName      => $k_awsTADom,
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
		last, if (!($retVal = sendPutAttrReqToSDB($reqHash)));
	}
	
	return $retVal;
}

sub procNU($)
{
    my $phid = shift;
    my $rHash = { DomainName => $k_awsUserDom, ItemName => $phid };
    my $resHash = undef;

    my $resp = sendReqToSDB($rHash, \&Amazon::SimpleDB::Client::getAttributes);

    if ($resp && $resp->isSetGetAttributesResult())
    {
        my $res = $resp->getGetAttributesResult();
        $rHash->{Attribute} = [ { Name => 'dateRegistered', Value => scalar(localtime()) } ];
        
        unless ($res->isSetAttribute() || ($resp = sendPutAttrReqToSDB($rHash)))
        {
            print T Dumper($resp) . "\n";
            $g_response = "Failure (Bad Registration)";
        }
        else
        {
            $resHash = {};
            foreach (@{$res->getAttribute()})
            {
                $resHash->{$_->getName()} = $_->getValue(), unless ($_->getName() eq 'psha');
            }
        }
    }

    return $resHash;
}

sub procNP($$$)
{
    my ($phid, $u, $p) = @_;
    # have to check if itemname=>$u exists in user table, if not then create it otherwise fail

    my $rHash = { DomainName => $k_awsUserDom, ItemName => $phid };

    $rHash->{Attribute} = [
        { Name => "name", Value => $u, Replace => 1 },
        { Name => "psha", Value => $p, Replace => 1 }
    ];

    return sendPutAttrReqToSDB($rHash);
}

sub procQWA($$)
{
    my ($phid, $dom) = @_;
    my $qDom = ($dom && $dom eq 'u' ? $k_awsUserDom : $k_awsTADom);

    my $qStr = "['deviceID' = '$phid']";
    my $rHash = { DomainName => $qDom, QueryExpression => $qStr };
    return sendReqToSDB($rHash, \&Amazon::SimpleDB::Client::queryWithAttributes);
}

#####
my $reqMethod = $g_q->request_method();
my $phid = $g_q->param('phid');
my $act = $g_q->param('act');

open (T, "+>>$k_logFile") or die "$k_logFile: $!\n\n";
print T "-----\n" . scalar(localtime()). "\n-----\n" . 
    "PhoneID:\t$phid\n";
    #. "TA Domain:\t$k_awsTADom\nUser Domain:\t$k_awsUserDom\n";

print T "Action:\t\t'$act' via '$reqMethod'\n";

if ($act eq 'qwa' && $phid)                     #query with attr, doesn't req. POST
{
    $g_response = Dumper(procQWA($phid, $g_q->param('d')));
}
elsif ($reqMethod && $reqMethod eq "POST")
{
    if ($phid) 
	{
        my $sha = $g_q->param('sha');
        my $json = decode_json($g_q->param('json')), if ($g_q->param('json'));

		if ($act eq 'ta' && $sha && $json)		# new transaction
		{
			$g_response = "Unable to process request.", unless (procTA($phid, $sha, $json));
		}
		elsif ($act eq 'nu')					# new user
		{
            $g_response = encode_json(procNU($phid));
	    }
        elsif ($act eq 'np')                    # new password
        {
            my $uname = $g_q->param('uname');
            my $phash = $g_q->param('psha');

            if ($uname && $phash)
            {
                $g_response = "Bad user add." unless (procNP($phid, $uname, $phash));
            }
            else
            {
                $g_response = "Error 500 Bad Arguments (Act=NP)";
            }
        }
		else
		{
            $g_response = "Error 500 Internal Server Error (Bad Arguments)";
		}
    }
    else
    {
        $g_response = "Error 406 Not Acceptable";
    }
}
else
{
    $g_response = "Error 405 Method Not Allowed";
}


print T "\nResponse:\t'$g_response'\n", if ($g_response && length($g_response) < 1024);
print T "\nElapsed:\t" . scalar(tv_interval($t0)) . "\n";
print T "-----\n\n";
close(T);

print $g_q->header();
print $g_response;
