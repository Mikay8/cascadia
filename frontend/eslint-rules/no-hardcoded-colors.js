// Flags color literals (hex, rgb/rgba, hsl/hsla) in JS and JSX string and template literals.
// Colors come from frontend/tokens/. Files inside tokens/ are exempt in eslint.config.js.
const COLOR = /#(?:[0-9a-f]{3,4}|[0-9a-f]{6}|[0-9a-f]{8})\b|\b(?:rgba?|hsla?)\s*\(/i;

const rule = {
  meta: {
    type: 'problem',
    docs: { description: 'Disallow hardcoded colors; use design tokens.' },
    messages: { hardcoded: 'Hardcoded color "{{value}}". Use a design token from frontend/tokens/.' },
    schema: [],
  },
  create(context) {
    function check(node, text) {
      const match = text.match(COLOR);
      if (match) context.report({ node, messageId: 'hardcoded', data: { value: match[0] } });
    }
    return {
      Literal(node) {
        if (typeof node.value === 'string') check(node, node.value);
      },
      TemplateElement(node) {
        check(node, node.value.raw);
      },
    };
  },
};

export default rule;
