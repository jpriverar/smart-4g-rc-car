%% From the squared error method, the obtained plant approximation
G = tf([0.07526 0.02277], [1 -0.7033 -0.1679], 0.01);
step(G)

%% Getting the cut-off frequency of the plant
bode(G)

wc = 4.4; % rad/s
fc = wc/(2*pi);

% Sampling frequency 5-8 times the cut-off frequency
fs = 5*fc;
ts = 1/fs;

%% Rewriting the plant with the new sampling period

Gc = d2c(G);
Gn = c2d(Gc, ts);

step(Gc)
hold on
step(G)
step(Gn)
hold off
legend("Continuous", "Discrete Raw", "Discrete Adjusted")

%% Creating PID with sisotool

sisotool(Gn)

%%
