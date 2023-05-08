%% From the squared error method, the obtained plant approximation
G = tf([0.1441 -0.1241], [1 -0.8606 -0.1211], 0.01);
step(G)

%% Getting the cut-off frequency of the plant
bode(G)

wc = 2; % rad/s
fc = wc/(2*pi);

% Sampling frequency 5-8 times the cut-off frequency
fs = 8*fc;
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
