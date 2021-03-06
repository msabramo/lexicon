import copy

from spec import Spec, eq_, ok_, raises, skip

from lexicon import AliasDict


class AliasDict_(Spec):
    class alias:
        def allows_aliasing_of_single_target_key(self):
            ad = AliasDict()
            ad.alias(from_='myalias', to='realkey')
            ad['realkey'] = 'value'
            eq_(ad['myalias'], 'value')

        def allows_aliasing_of_multiple_target_keys(self):
            ad = AliasDict()
            ad.alias(from_='myalias', to=('key1', 'key2'))
            ad['key1'] = ad['key2'] = False
            assert not ad['key1']
            ad['myalias'] = True
            assert ad['key1'] and ad['key2']

    class unalias:
        def unsets_aliases(self):
            ad = AliasDict()
            ad['realkey'] = 'value'
            ad.alias('myalias', to='realkey')
            eq_(ad['myalias'], 'value')
            ad.unalias('myalias')
            assert 'myalias' not in ad

        @raises(KeyError)
        def raises_KeyError_on_nonexistent_alias(self):
            ad = AliasDict()
            ad.unalias('lol no')

    def membership_tests(self):
        ad = AliasDict()
        ad.alias('myalias', to='realkey')
        ad['realkey'] = 'value'
        assert 'myalias' in ad

    def key_deletion(self):
        ad = AliasDict()
        ad.alias('myalias', to='realkey')
        ad['realkey'] = 'value'
        assert 'realkey' in ad
        del ad['myalias']
        assert 'realkey' not in ad
        assert 'myalias' not in ad

    @raises(ValueError)
    def access_to_multi_target_aliases_is_undefined(self):
        ad = AliasDict()
        ad.alias('myalias', to=('key1', 'key2'))
        ad['key1'] = ad['key2'] = 5
        ad['myalias']

    class dangling_aliases:
        "dangling aliases"
        @raises(KeyError)
        def raise_KeyError_on_access(self):
            ad = AliasDict()
            ad.alias('myalias', to='realkey')
            assert 'realkey' not in ad
            ad['myalias']

        @raises(KeyError)
        def caused_by_removal_of_target_key(self):
            # TODO: this test probably false-passes if any line but the last raises
            # KeyError by accident...
            ad = AliasDict()
            ad.alias('myalias', to='realkey')
            ad['realkey'] = 'value'
            assert 'realkey' in ad
            eq_(ad['myalias'], 'value')
            del ad['realkey']
            ad['myalias']

    class recursive_aliasing:
        "recursive aliasing"
        def _recursive_aliases(self):
            ad = AliasDict()
            ad.alias('alias1', to='realkey')
            ad.alias('alias2', to='alias1')
            ad['alias2'] = 'value'
            assert ad['alias1'] == ad['alias2'] == ad['realkey'] == 'value'
            return ad

        def works_in_base_case(self):
            self._recursive_aliases()

        def unalias_is_not_recursive(self):
            ad = self._recursive_aliases()
            ad.unalias('alias2')
            assert 'alias1' in ad
            eq_(ad['alias1'], 'value')

        def deletion_is_recursive(self):
            ad = self._recursive_aliases()
            del ad['alias2']
            assert 'realkey' not in ad
            ad['realkey'] = 'newvalue'
            assert 'alias1' in ad
            eq_(ad['alias1'], 'newvalue')

    def deepcopy_copies_aliases_correctly(self):
        a1 = AliasDict({'key1': 'val1', 'key2': 'val2'})
        a1.alias('myalias', to='key1')
        eq_(a1['myalias'], 'val1')
        a2 = copy.deepcopy(a1)
        assert 'key1' in a2
        eq_(a2['key2'], 'val2')
        a1.unalias('myalias')
        assert 'myalias' not in a1
        assert 'myalias' in a2
        eq_(a2['myalias'], 'val1')
