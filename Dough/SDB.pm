package Dough::SDB;

use Amazon::SimpleDB::Client;

use Dough::Config;
use Dough::Log;

sub new {
	my $class = shift;
	my $self = {};

	bless($self, $class);
    $self->{conn} = Amazon::SimpleDB::Client->new($k_awsKey, $k_awsSec);
    $self->{l} = Dough::Log->instance();

	return defined($self->{conn}) ? $self : undef;
}

sub __sendRequest {
    my ($s, $reqHash, $reqFunc) = @_;
    my $retVal;
    
    print STDERR "__sendRequest($s, $reqHash, $reqFunc)\n";
    eval
	{
        $s->{l}->log("Domain:\t\t" . $reqHash->{DomainName});

		my $resp = &$reqFunc($s->{conn}, $reqHash);
		
		if ($resp->isSetResponseMetadata() && (my $rMeta = $resp->getResponseMetadata()))
		{
			$s->{l}->log("ItemName:\t" . ($reqHash->{ItemName})), if ($reqHash->{ItemName});
			$s->{l}->log("RequestID:\t" . ($rMeta->getRequestId())), if ($rMeta->isSetRequestId());
			$s->{l}->log("BoxUsage:\t" . ($rMeta->getBoxUsage())), if ($rMeta->isSetBoxUsage());
		}

        $retVal = $resp;
	};
	
	if ((my $ex = $@))
	{
		require Amazon::SimpleDB::Exception;
        require Data::Dumper;
		$s->{l}->debug("\nException: " . Data::Dumper::Dumper($ex));
		$s->{l}->debug("Request: " . Data::Dumper::Dumper($reqHash));
	    $retVal = undef;
	}
	
	return $retVal;

}

sub putAttrs {
    return $_[0]->__sendRequest($_[1], \&Amazon::SimpleDB::Client::putAttributes);
}

sub getAttrs {
    return $_[0]->__sendRequest($_[1], \&Amazon::SimpleDB::Client::getAttributes);
}

sub queryWithAttrs {
    return $_[0]->__sendRequest($_[1], \&Amazon::SimpleDB::Client::queryWithAttributes);
}

1;
