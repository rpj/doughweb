package Dough::SDB;

use Amazon::SimpleDB::Client;

use Dough::Config;

sub new {
	my $class = shift;
	my $self = {};

	bless($self, $class);
	return $self;
}

1;
