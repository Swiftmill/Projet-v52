window.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.toast').forEach((toast) => {
    setTimeout(() => {
      toast.classList.add('hide');
    }, 4000);
  });

  document.querySelectorAll('[data-step-form]').forEach((form) => {
    const steps = Array.from(form.querySelectorAll('[data-step]'));
    const stepOrder = steps.map((step) => step.dataset.step);
    const typeInputs = Array.from(form.querySelectorAll('input[name="is_series"]'));
    const nextButton = form.querySelector('[data-next-step]');
    const prevButton = form.querySelector('[data-prev-step]');
    const filmOnlyBlock = form.querySelector('[data-film-only]');
    const filmRequiredInput = form.querySelector('[data-film-required]');
    const seriesHint = form.querySelector('[data-series-hint]');
    const stepIndicators = Array.from(form.querySelectorAll('[data-step-indicator]'));

    const getSelectedType = () => typeInputs.find((input) => input.checked);
    const isSeriesSelected = () => {
      const selected = getSelectedType();
      return selected ? selected.value === '1' : false;
    };

    const refreshIndicators = (activeStep) => {
      const activeIndex = stepOrder.indexOf(activeStep);
      stepIndicators.forEach((indicator) => {
        const key = indicator.dataset.stepIndicator;
        indicator.classList.remove('is-active', 'is-complete', 'is-disabled');

        if (key === 'episodes') {
          if (isSeriesSelected()) {
            indicator.classList.add(activeStep === 'details' ? 'is-active' : 'is-complete');
          } else {
            indicator.classList.add('is-disabled');
          }
          return;
        }

        if (key === activeStep) {
          indicator.classList.add('is-active');
          return;
        }

        const indicatorIndex = stepOrder.indexOf(key);
        if (indicatorIndex !== -1 && activeIndex > indicatorIndex) {
          indicator.classList.add('is-complete');
        }
      });
    };

    const setStep = (stepName) => {
      form.dataset.currentStep = stepName;
      steps.forEach((step) => {
        const isActive = step.dataset.step === stepName;
        step.hidden = !isActive;
      });
      refreshIndicators(stepName);
    };

    const syncOptionCards = () => {
      typeInputs.forEach((input) => {
        const card = input.closest('.option-card');
        if (!card) return;
        card.classList.toggle('is-selected', input.checked);
      });
    };

    const updateTypeState = () => {
      const selected = getSelectedType();
      const isSeries = !!selected && selected.value === '1';

      if (nextButton) {
        nextButton.disabled = !selected;
      }

      if (filmOnlyBlock) {
        filmOnlyBlock.classList.toggle('is-hidden', isSeries);
      }

      if (filmRequiredInput) {
        if (isSeries) {
          filmRequiredInput.removeAttribute('required');
        } else {
          filmRequiredInput.setAttribute('required', 'required');
        }
      }

      if (seriesHint) {
        seriesHint.classList.toggle('is-hidden', !isSeries);
      }

      syncOptionCards();
      refreshIndicators(form.dataset.currentStep || stepOrder[0]);
    };

    const initialStep = form.dataset.currentStep || form.dataset.initialStep || stepOrder[0] || 'type';
    steps.forEach((step) => {
      step.hidden = step.dataset.step !== initialStep;
    });
    refreshIndicators(initialStep);
    updateTypeState();

    if (nextButton) {
      nextButton.addEventListener('click', () => {
        setStep('details');
      });
    }

    if (prevButton) {
      prevButton.addEventListener('click', () => {
        setStep('type');
        if (typeInputs.length) {
          typeInputs[0].focus();
        }
      });
    }

    typeInputs.forEach((input) => {
      input.addEventListener('change', () => {
        updateTypeState();
        if (form.dataset.currentStep === 'type' && nextButton && !nextButton.disabled) {
          nextButton.focus();
        }
      });
    });
  });
});
