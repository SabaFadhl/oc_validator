from json import load
from os.path import join, dirname, abspath


class RuleEngine:
    def __init__(self, helper, wellformed):
        self.helper = helper
        self.wellformed = wellformed
        script_dir = dirname(abspath(__file__))
        rules_path = join(script_dir, 'rules', 'meta_rules.json')
        with open(rules_path, 'r', encoding='utf-8') as f:
            self.meta_rules = load(f)

    def apply_field_rules(self, field_name, value, row_idx, messages):
        errors = []

        for rule in self.meta_rules:
            if rule.get('field') != field_name:
                continue

            if not value:
                continue

            if self._evaluate_rule(rule, value):
                message = messages[rule['message_key']]
                table = {row_idx: {field_name: [rule.get('table_index', 0)]}}

                errors.append(
                    self.helper.create_error_dict(
                        validation_level=rule['validation_level'],
                        error_type=rule['error_type'],
                        message=message,
                        error_label=rule['error_label'],
                        located_in=rule['located_in'],
                        table=table,
                        valid=rule['valid']
                    )
                )

        return errors

    def _evaluate_rule(self, rule, value):
        rule_type = rule.get('rule_type')
        condition = rule.get('condition')

        if rule_type == 'string_check':
            if condition == 'is_all_caps':
                return value.isupper()

        if rule_type == 'function_check':
            if condition == 'check_page_interval_false':
                if not self.wellformed.wellformedness_page(value):
                    return False
                return not self.wellformed.check_page_interval(value)
        return False