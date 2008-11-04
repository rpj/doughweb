package Dough::CGI::Process;

use Exporter qw(import);

use Dough::Config;
use Dough::CGI;
use Dough::SDB;

use Digest::SHA qw(sha1_hex);

@EXPORT = qw(qwa);

sub qwa {
    my ($cgi) = @_;
	print STDERR "CGI obj: $cgi\n";

    my $phid = $cgi->{phid};
    my $dom = $cgi->{q}->param('d');
    my $qDom = ($dom && $dom eq 'u' ? $k_awsUserDom : $k_awsTADom);

    my $qStr = "['deviceID' = '$phid']";
    my $rHash = { DomainName => $qDom, QueryExpression => $qStr };
    
    my $_r = $cgi->{sdb}->queryWithAttrs($rHash);
    $cgi->{l}->log("QWA ret: $_r");

    return {};
}

sub ta {
    my ($cgi) = @_;

    my $phid = $cgi->{phid};
    my $sha = $cgi->{sha};
    my $json = $cgi->{json};

	my $checkSha = sha1_hex($cgi->{q}->param('json'));
	my $parityFault = ($sha eq $checkSha) ? 0 : 1;
    my $retVal = {};
	
	$cgi->{l}->log("SHA-1 Check:\t$sha vs $checkSha ($parityFault)");
	
    eval {
        foreach my $jHash (@{$json})
        {
            my $jSha = sha1_hex(%{$jHash});
            my $tHex = sha1_hex(time());
            my $reqHash = {
                DomainName      => $k_awsTADom,
                ItemName        => substr($tHex, 0, 8) . "-" . substr($tHex, length($tHex) - 4, 4) . "-" .
                                    substr($phid, 0, 4) . "-" . substr($checkSha, rand(length($checkSha) - 6), 4) . "-" .
                                    substr($jSha, 0, 12),
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
                            if ($k_whereConcreteSaveKeys->{$wcKey})
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
            last, if (!($cgi->{sdb}->putAttrs($reqHash)));
        }
    };  #eval

    if ($@) {
        my $es = ($@ =~ /Not an ARRAY/i) ? "Malformed JSON." : "Unknown error.";
        $retVal = { 'Error' => "$es" };
    }
	
	return $retVal;
}
1;
