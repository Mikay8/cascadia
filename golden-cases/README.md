# Golden cases

Real past runs converted to fixtures (increment 0.2). Each case holds the inputs and the expected outputs of one period, and defines correct engine output.

Rules:

- Never change an expected output to make a test pass. A failing case means the code is wrong or a human must review the case.
- Money values are strings in decimal notation (for example `"1234.56"`), never JSON numbers.
- Partner data must be anonymized before it is checked in. No real names, account numbers, or secrets.

The file format is set in increment 0.2.
